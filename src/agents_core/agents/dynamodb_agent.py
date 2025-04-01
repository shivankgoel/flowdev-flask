import logging
from typing import Dict, Any, Optional
from src.inference import InferenceClient
from src.specs.dynamodb_spec import DynamoDBTableSpec
from src.specs.flow_canvas_spec import ProgrammingLanguage, CanvasNodeSpec
from ..prompts.prompt_formatters.dynamodb_formatter import DynamoDBPromptFormatter
from ..llm_response_parsers.dynamodb_parser import DynamoDBParser
from .models.agent_models import AgentStep

logger = logging.getLogger(__name__)


class DynamoDBAgent:
    def __init__(
        self,
        inference_client: InferenceClient,
        current_node: CanvasNodeSpec,
        programming_language: ProgrammingLanguage
    ):
        self.inference_client = inference_client
        self.current_node = current_node
        self.programming_language = programming_language
        self.logger = logger
        self.parser = DynamoDBParser()
        self.formatter = DynamoDBPromptFormatter()

    def _get_table_spec(self) -> DynamoDBTableSpec:
        """Extract DynamoDB table spec from the current node."""
        if not isinstance(self.current_node.data.spec, DynamoDBTableSpec):
            raise ValueError("Node data spec must be of type DynamoDBTableSpec")
        return self.current_node.data.spec

    def _log_step(self, step: AgentStep, details: Dict[str, Any], error: Optional[str] = None) -> None:
        """Log an agent step with details."""
        if error:
            self.logger.error(f"{step.value}: {error}", extra=details)
        else:
            self.logger.info(step.value, extra=details)

    async def generate_code(self) -> str:
        """Generate DynamoDB table code."""
        try:
            spec = self._get_table_spec()
            
            # Format prompt
            prompt = self.formatter.format_prompt(spec, self.programming_language.value)
            self._log_step(AgentStep.FORMAT_PROMPT, {"table_name": spec.name})

            # Generate code
            response = await self.inference_client.generate(prompt)
            self._log_step(AgentStep.GENERATE, {"table_name": spec.name})

            # Parse response
            result = self.parser.parse(response, self.programming_language.value)
            self._log_step(AgentStep.PARSE, {"code_length": len(result.code)})

            return result.code

        except Exception as e:
            self._log_step(AgentStep.ERROR, {"error": str(e)}, str(e))
            raise ValueError(f"Failed to generate code: {str(e)}") 