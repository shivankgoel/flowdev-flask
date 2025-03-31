import os
from typing import List, Any, Dict, Optional
from specs.dynamodb_spec import DynamoDBTableSpec
from specs.flow_canvas_spec import ProgrammingLanguage
from .base_agent import BaseSpecAgent, GenerationFeedback, AgentStep, AgentObservation
from .prompts.formatted_prompts.dynamodb import (
    JavaDynamoDBFormatter,
    PythonDynamoDBFormatter,
    TypeScriptDynamoDBFormatter
)
from .parsers.dynamodb_parser import (
    JavaDynamoDBParser,
    PythonDynamoDBParser,
    TypeScriptDynamoDBParser
)

class DynamoDBAgent(BaseSpecAgent):
    def __init__(
        self,
        inference_client,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        observation_callback: Optional[callable] = None
    ):
        super().__init__(inference_client, max_retries, retry_delay, observation_callback)
        self.template_dir = os.path.join(
            os.path.dirname(__file__),
            'prompts',
            'prompt_templates',
            'dynamodb'
        )
        self.formatted_prompt_dir = os.path.join(
            os.path.dirname(__file__),
            'prompts',
            'formatted_prompts',
            'dynamodb'
        )
        
        # Map programming languages to their formatters and parsers
        self.formatters = {
            ProgrammingLanguage.JAVA: JavaDynamoDBFormatter,
            ProgrammingLanguage.PYTHON: PythonDynamoDBFormatter,
            ProgrammingLanguage.TYPESCRIPT: TypeScriptDynamoDBFormatter
        }
        
        self.parsers = {
            ProgrammingLanguage.JAVA: JavaDynamoDBParser(),
            ProgrammingLanguage.PYTHON: PythonDynamoDBParser(),
            ProgrammingLanguage.TYPESCRIPT: TypeScriptDynamoDBParser()
        }
        
        # Store current template for retries
        self.current_template = None
        self.current_formatted_data = None
        self.current_programming_language = None
        
    def generate_code(self, spec: DynamoDBTableSpec, input_specs: List[Any], programming_language: ProgrammingLanguage) -> str:
        """
        Generate DynamoDB table code based on the spec and input specs.
        
        Args:
            spec: The DynamoDB table spec
            input_specs: List of specs from input nodes (not used for DynamoDB)
            programming_language: The programming language to generate code in
            
        Returns:
            str: Generated code
        """
        self.current_programming_language = programming_language
        
        # Get language-specific template path and formatter
        template_path = os.path.join(self.template_dir, f"{programming_language.value}.txt")
        formatter = self.formatters[programming_language]
        
        self._observe(AgentStep.LOAD_TEMPLATE, {
            "template_path": template_path,
            "programming_language": programming_language.value,
            "table_name": spec.table_name
        })
        
        # Load and format the prompt template
        self.current_template = self._load_prompt_template(template_path)
        self.current_formatted_data = formatter.format_prompt(spec)
        
        self._observe(AgentStep.FORMAT_PROMPT, {
            "template_length": len(self.current_template),
            "formatted_data_keys": list(self.current_formatted_data.keys()),
            "table_name": spec.table_name,
            "primary_key": spec.primary_key
        })
        
        prompt = self._format_prompt(self.current_template, **self.current_formatted_data)
        
        # Create formatted prompts directory if it doesn't exist
        os.makedirs(self.formatted_prompt_dir, exist_ok=True)
        
        # Save the formatted prompt
        formatted_prompt_path = os.path.join(
            self.formatted_prompt_dir,
            f"{programming_language.value}_prompt.txt"
        )
        self._save_formatted_prompt(prompt, formatted_prompt_path)
        
        # Get response from LLM
        self._observe(AgentStep.GENERATE_CODE, {
            "prompt_length": len(prompt),
            "table_name": spec.table_name
        })
        response = self.inference_client.generate(prompt)
        
        # Parse and return the code
        return self.parse_response(response, spec.table_name, spec.primary_key, programming_language)
        
    def parse_response(self, response: str, table_name: str, primary_key: str, programming_language: ProgrammingLanguage) -> str:
        """
        Parse the LLM response to extract the generated code.
        
        Args:
            response: Raw response from the LLM
            table_name: The DynamoDB table name
            primary_key: The primary key name
            programming_language: The programming language of the generated code
            
        Returns:
            str: Parsed code
            
        Raises:
            ValueError: If response parsing fails
        """
        self._observe(AgentStep.PARSE_RESPONSE, {
            "response_length": len(response),
            "table_name": table_name,
            "primary_key": primary_key,
            "programming_language": programming_language.value
        })
        
        parser = self.parsers[programming_language]
        try:
            result = parser.parse(response, table_name, primary_key)
            
            self._observe(AgentStep.VALIDATE_CODE, {
                "code_length": len(result.code),
                "imports_count": len(result.imports),
                "table_name": table_name
            })
            
            return result.code
        except ValueError as e:
            # Create feedback from the error
            feedback = self._create_feedback_from_error(str(e))
            self._observe(AgentStep.ERROR, {
                "error": str(e),
                "feedback": str(feedback),
                "table_name": table_name
            }, str(e))
            raise ValueError(f"Failed to parse DynamoDB code: {str(e)}", feedback)
            
    def _create_feedback_from_error(self, error_message: str) -> GenerationFeedback:
        """
        Create feedback from an error message.
        
        Args:
            error_message: The error message
            
        Returns:
            GenerationFeedback: Feedback object
        """
        feedback = GenerationFeedback(error_message=error_message)
        
        # Extract missing imports
        if "No DynamoDB imports found" in error_message:
            feedback.missing_imports = ["DynamoDB", "DynamoDBClient"]
            
        # Extract missing patterns
        if "No AWS SDK" in error_message:
            feedback.missing_patterns = ["DynamoDBClient", "DynamoDBDocumentClient"]
        elif "No boto3 patterns" in error_message:
            feedback.missing_patterns = ["boto3.client('dynamodb')", "boto3.resource('dynamodb')"]
            
        # Extract validation errors
        if "not found in code" in error_message:
            feedback.validation_errors = [error_message]
            
        self._observe(AgentStep.RETRY, {
            "error_message": error_message,
            "feedback": str(feedback)
        })
            
        return feedback
        
    def _update_prompt_with_feedback(self, feedback: GenerationFeedback) -> None:
        """
        Update the prompt template based on feedback.
        
        Args:
            feedback: Feedback from previous generation attempt
        """
        if not self.current_template or not self.current_formatted_data:
            return
            
        self._observe(AgentStep.RETRY, {
            "feedback": str(feedback),
            "current_template_length": len(self.current_template)
        })
            
        # Add missing imports to the template
        if feedback.missing_imports:
            imports_section = "\n".join([
                f"import {imp};" for imp in feedback.missing_imports
            ])
            self.current_formatted_data["imports"] = imports_section
            
        # Add missing patterns as examples
        if feedback.missing_patterns:
            patterns_section = "\n".join([
                f"// Example: {pattern}" for pattern in feedback.missing_patterns
            ])
            self.current_formatted_data["examples"] = patterns_section
            
        # Add validation errors as requirements
        if feedback.validation_errors:
            requirements_section = "\n".join([
                f"// Required: {error}" for error in feedback.validation_errors
            ])
            self.current_formatted_data["requirements"] = requirements_section
            
        self._observe(AgentStep.FORMAT_PROMPT, {
            "updated_template_length": len(self.current_template),
            "feedback_applied": True
        })
        
    def _format_attributes(self, attributes: List[Any]) -> str:
        """
        Format the DynamoDB attributes for the prompt.
        
        Args:
            attributes: List of DynamoDB attributes
            
        Returns:
            str: Formatted attributes string
        """
        return "\n".join([
            f"- {attr.name}: {attr.type}"
            for attr in attributes
        ]) 