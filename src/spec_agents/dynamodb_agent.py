import os
from typing import List, Any, Dict, Optional
from src.specs.dynamodb_spec import DynamoDBTableSpec
from src.specs.flow_canvas_spec import ProgrammingLanguage, CanvasNodeSpec, NodeDataSpec
from .base_agent import BaseSpecAgent, CodeFeedback, FeedbackType, AgentStep
from .prompts.formatted_prompts.dynamodb import (
    JavaDynamoDBFormatter,
    PythonDynamoDBFormatter,
    TypeScriptDynamoDBFormatter
)
from .parsers.dynamodb_parser import DynamoDBParser
import logging

logger = logging.getLogger(__name__)

class DynamoDBAgent(BaseSpecAgent):
    def __init__(
        self,
        inference_client,
        current_node: CanvasNodeSpec,
        programming_language: ProgrammingLanguage,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        super().__init__(inference_client, current_node, programming_language, max_retries, retry_delay)
        
        # Initialize formatters and parser
        self.formatters = {
            ProgrammingLanguage.JAVA: JavaDynamoDBFormatter(),
            ProgrammingLanguage.PYTHON: PythonDynamoDBFormatter(),
            ProgrammingLanguage.TYPESCRIPT: TypeScriptDynamoDBFormatter()
        }
        self.parser = DynamoDBParser()
        
    def _create_prompt_data(self) -> Dict[str, Any]:
        """Create prompt data dictionary from node spec."""
        if not isinstance(self.current_node.data.spec, DynamoDBTableSpec):
            raise ValueError("Node data spec must be of type DynamoDBTableSpec")
            
        spec = self.current_node.data.spec
        return {
            "name": spec.name,
            "hash_key": spec.hash_key,
            "range_key": spec.range_key,
            "attributes": spec.attributes,
            "feedback_history": self.feedback_history
        }
        
    def _add_feedback_for_error(self, error_message: str, retry_count: int) -> None:
        """Add feedback to history based on error message."""
        feedback_list = []
        
        # Check for missing imports
        if "No DynamoDB imports found" in error_message:
            feedback_list.append(CodeFeedback(
                feedback_type=FeedbackType.MISSING_IMPORT,
                message="Missing DynamoDB imports",
                details={"required_imports": ["DynamoDB", "DynamoDBClient"]}
            ))
            
        # Check for missing SDK patterns
        if "No AWS SDK" in error_message:
            feedback_list.append(CodeFeedback(
                feedback_type=FeedbackType.MISSING_PATTERN,
                message="Missing AWS SDK patterns",
                details={"required_patterns": ["DynamoDBClient", "DynamoDBDocumentClient"]}
            ))
        elif "No boto3 patterns" in error_message:
            feedback_list.append(CodeFeedback(
                feedback_type=FeedbackType.MISSING_PATTERN,
                message="Missing boto3 patterns",
                details={"required_patterns": ["boto3.client('dynamodb')", "boto3.resource('dynamodb')"]}
            ))
            
        # Check for validation errors
        if "not found in code" in error_message:
            feedback_list.append(CodeFeedback(
                feedback_type=FeedbackType.VALIDATION_ERROR,
                message=error_message
            ))
            
        # Add general error if no specific feedback was created
        if not feedback_list:
            feedback_list.append(CodeFeedback(
                feedback_type=FeedbackType.ERROR,
                message=error_message
            ))
            
        # Store feedback in history
        self._store_feedback(retry_count, feedback_list)
        
    async def generate_code(
        self, 
        retry_count: int = 0
    ) -> str:
        """Generate DynamoDB table code based on the node spec."""
        # Get language-specific formatter
        formatter = self.formatters[self.programming_language]
        
        # Create and format prompt
        prompt_data = self._create_prompt_data()
        prompt = formatter.format_prompt(**prompt_data)
        
        # Log prompt generation
        self._log_step(AgentStep.FORMAT_PROMPT, {
            "table_name": self.current_node.data.spec.name,
            "primary_key": self.current_node.data.spec.hash_key,
            "sort_key": self.current_node.data.spec.range_key
        })
        
        # Generate code using LLM
        response = await self.inference_client.generate(prompt)
        self._log_step(AgentStep.GENERATE_CODE, {
            "prompt_length": len(prompt),
            "table_name": self.current_node.data.spec.name
        })
        
        # Parse and return the code
        return self.parse_response(response, retry_count)
        
    def parse_response(self, response: str, retry_count: int) -> str:
        """Parse the LLM response to extract the generated code."""
        try:
            # Parse the response
            result = self.parser.parse(response, self.programming_language.value)
            
            # Log successful parsing
            self._log_step(AgentStep.VALIDATE_CODE, {
                "code_length": len(result.code),
                "imports_count": len(result.imports)
            })
            
            return result.code
            
        except ValueError as e:
            # Add feedback to history based on error
            self._add_feedback_for_error(str(e), retry_count)
            
            # Log error
            self._log_step(AgentStep.ERROR, {
                "error": str(e),
                "retry_count": retry_count
            }, str(e))
            
            # Raise error
            raise ValueError(f"Failed to parse DynamoDB code: {str(e)}") 