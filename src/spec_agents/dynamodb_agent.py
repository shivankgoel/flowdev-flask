import os
from typing import List, Any, Dict
from src.specs.dynamodb_spec import DynamoDBTableSpec
from src.specs.flow_canvas_spec import ProgrammingLanguage, CanvasNodeSpec
from .base_agent import BaseSpecAgent, AgentStep
from .parsers import CodeParser
from .prompts.formatted_prompts.dynamodb.java_formatter import JavaDynamoDBFormatter
from .prompts.formatted_prompts.dynamodb.python_formatter import PythonDynamoDBFormatter
from .prompts.formatted_prompts.dynamodb.typescript_formatter import TypeScriptDynamoDBFormatter
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
        self.parser = CodeParser()
        
        # Initialize language-specific formatter
        self.formatters = {
            ProgrammingLanguage.JAVA: JavaDynamoDBFormatter(),
            ProgrammingLanguage.PYTHON: PythonDynamoDBFormatter(),
            ProgrammingLanguage.TYPESCRIPT: TypeScriptDynamoDBFormatter()
        }
        self.formatter = self.formatters[programming_language]
        
    def _create_prompt_data(self) -> Dict[str, Any]:
        """Create prompt data dictionary from node spec."""
        if not isinstance(self.current_node.data.spec, DynamoDBTableSpec):
            raise ValueError("Node data spec must be of type DynamoDBTableSpec")
            
        spec = self.current_node.data.spec
        
        # Convert attributes to simple dictionary
        attributes = [{
            "name": attr.name,
            "type": str(attr.type)
        } for attr in spec.attributes]
        
        # Create prompt data with all fields
        prompt_data = {
            "name": spec.name,
            "attributes": attributes,
            "hash_key": spec.hash_key,
            "range_key": spec.range_key or None,  # Ensure default value is passed
            "infra_spec": {
                "billing_mode": str(spec.infra_spec.billing_mode) if spec.infra_spec else None,
                "encryption": spec.infra_spec.encryption if spec.infra_spec else False
            } if spec.infra_spec else None
        }
        
        return prompt_data
        
    async def generate_code(
        self, 
        retry_count: int = 0
    ) -> str:
        """Generate DynamoDB table code based on the node spec."""
        # Create and format prompt
        prompt_data = self._create_prompt_data()
        prompt = self.formatter.format_prompt(**prompt_data)
        
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
            # Log error
            self._log_step(AgentStep.ERROR, {
                "error": str(e),
                "retry_count": retry_count
            }, str(e))
            
            # Raise error
            raise ValueError(f"Failed to parse DynamoDB code: {str(e)}") 