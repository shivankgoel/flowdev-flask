import logging
from typing import Dict, Any, Optional
from src.inference import InferenceClient
from src.inference.models.inference_models import InferenceResponse, ToolCall
from src.specs.dynamodb_spec import DynamoDBTableSpec
from src.specs.flow_canvas_spec import ProgrammingLanguage, CanvasNodeSpec, CanvasDefinitionSpec
from ..prompts.prompt_formatters.dynamodb_formatter import DynamoDBPromptFormatter
from ..prompts.utils.spec_formatters import CanvasToPrompt, NodeSpecToPrompt, DynamoDBTableToPrompt
from ..llm_response_parsers.dynamodb_parser import DynamoDBParser
from .models.agent_models import AgentStep, CodingAgentResponse

logger = logging.getLogger(__name__)


class DynamoDBAgent:
    def __init__(
        self,
        inference_client: InferenceClient,
        current_node_id: str,
        canvas: CanvasDefinitionSpec,
    ):
        self.inference_client = inference_client
        self.current_node_id = current_node_id
        self.canvas = canvas
        self.logger = logger
        self.parser = DynamoDBParser()
        self.formatter = DynamoDBPromptFormatter()

    def _get_table_spec(self) -> DynamoDBTableSpec:
        """Extract DynamoDB table spec from the current node."""
        current_node = self.canvas.nodes.get(self.current_node_id)
        if not current_node:
            raise ValueError(f"Node with id {self.current_node_id} not found in canvas")
            
        if not isinstance(current_node.data.spec, DynamoDBTableSpec):
            raise ValueError("Node data spec must be of type DynamoDBTableSpec")
        return current_node.data.spec

    def _log_step(self, step: AgentStep, details: Dict[str, Any], error: Optional[str] = None) -> None:
        """Log an agent step with details."""
        if error:
            self.logger.error(f"{step.value}: {error}", extra=details)
        else:
            self.logger.info(step.value, extra=details)

    def _handle_tool_calls(self, tool_calls: list[ToolCall]) -> CodingAgentResponse:
        """Handle tool calls from the inference response."""
        # For now, we don't support tool calls in DynamoDB agent
        return CodingAgentResponse(code="", error="Tool calls are not supported in DynamoDB agent")

    async def generate_code(
        self,
        instruction_source: str = "",
        instructions: str = "",
        previous_code: str = ""
    ) -> CodingAgentResponse:
        """Generate DynamoDB table code."""
        try:
            # Format prompt
            prompt = self.formatter.format_prompt(
                spec=self._get_table_spec(),  # Only needed for type checking
                language=self.canvas.programming_language.value,
                current_node_id=self.current_node_id,
                canvas=self.canvas,
                instruction_source=instruction_source,
                instructions=instructions,
                previous_code=previous_code
            )
            self._log_step(AgentStep.FORMAT_PROMPT, {"table_name": self._get_table_spec().name})

            # Generate code
            response = await self.inference_client.generate(prompt)
            self._log_step(AgentStep.GENERATE, {"table_name": self._get_table_spec().name})

            # Handle different response types
            if response.error:
                return CodingAgentResponse(code="", error=f"Inference error: {response.error}")

            if response.tool_calls:
                return self._handle_tool_calls(response.tool_calls)

            if not response.text_response:
                return CodingAgentResponse(code="", error="No text response received from inference")

            # Log the raw response for debugging
            self.logger.debug(f"Raw response from inference: {response.text_response}")

            # Parse response
            try:
                result = self.parser.parse(response.text_response, self.canvas.programming_language.value)
                self._log_step(AgentStep.PARSE, {"code_length": len(result.code)})
                return CodingAgentResponse(code=result.code)
            except ValueError as e:
                self.logger.error(f"Failed to parse code: {str(e)}")
                return CodingAgentResponse(code="", error=f"Failed to parse code: {str(e)}")

        except Exception as e:
            self._log_step(AgentStep.ERROR, {"error": str(e)}, str(e))
            return CodingAgentResponse(code="", error=f"Failed to generate code: {str(e)}") 