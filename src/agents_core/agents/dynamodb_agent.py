import logging
from typing import Dict, Any, Optional
from src.inference import BaseLLMInference
from src.inference.models.inference_models import InferenceResponse, ToolCall
from src.specs.dynamodb_spec import DynamoDBTableSpec
from src.specs.flow_canvas_spec import ProgrammingLanguage, CanvasNodeSpec, CanvasDefinitionSpec
from ..prompts.prompt_formatters.dynamodb_formatter import DynamoDBPromptFormatter
from ..prompts.utils.spec_formatters import CanvasToPrompt, NodeSpecToPrompt, DynamoDBTableToPrompt
from ..llm_response_parsers.dynamodb_parser import DynamoDBParser
from ..llm_response_parsers.models.parser_models import ParsedResponse
from .models.agent_models import AgentStep, AgentResponse, AgentThoughts
from .models.agent_common import AgentCommon

logger = logging.getLogger(__name__)


class DynamoDBAgent:
    def __init__(
        self,
        inference_client: BaseLLMInference,
        current_node_id: str,
        canvas: CanvasDefinitionSpec,
        send_message_handler: callable
    ):
        self.inference_client = inference_client
        self.current_node_id = current_node_id
        self.canvas = canvas
        self.common = AgentCommon(
            inference_client=inference_client,
            current_node_id=current_node_id,
            canvas=canvas
        )
        self.parser = DynamoDBParser()
        self.formatter = DynamoDBPromptFormatter()
        
        # Set handlers for common tools
        self.common.set_handlers(send_message_handler)

    def _get_table_spec(self) -> DynamoDBTableSpec:
        """Extract DynamoDB table spec from the current node."""
        current_node = self.canvas.nodes.get(self.current_node_id)
        if not current_node:
            raise ValueError(f"Node with id {self.current_node_id} not found in canvas")
            
        if not isinstance(current_node.data.spec, DynamoDBTableSpec):
            raise ValueError("Node data spec must be of type DynamoDBTableSpec")
        return current_node.data.spec

    async def invoke_agent(
        self,
        instruction_source: str = "",
        instructions: str = "",
        previous_code: str = ""
    ) -> AgentResponse:
        """Invoke the agent with instructions and return the response."""
        try:
            # Format prompt
            prompt = self.formatter.format_prompt(
                spec=self._get_table_spec(),
                language=self.canvas.programming_language.value,
                current_node_id=self.current_node_id,
                canvas=self.canvas,
                instruction_source=instruction_source,
                instructions=instructions,
                previous_code=previous_code
            )
            self.common.log_step(AgentStep.FORMAT_PROMPT, {"table_name": self._get_table_spec().name})

            # Generate response
            response = await self.inference_client.generate(prompt)
            self.common.log_step(AgentStep.GENERATE, {"table_name": self._get_table_spec().name})

            # Handle different response types
            if response.error:
                return self.common.create_error_response(f"Inference error: {response.error}")

            if response.tool_calls:
                responses = await self.common.handle_tool_calls(response.tool_calls)
                # For now, just return the first response
                return responses[0] if responses else self.common.create_error_response("No responses from tool calls")

            if not response.text_response:
                return self.common.create_error_response("No text response received from inference")

            # Log the raw response for debugging
            self.common.logger.debug(f"Raw response from inference: {response.text_response}")

            # Parse response
            try:
                parsed_response = self.parser.parse(response.text_response, self.canvas.programming_language.value)
                self.common.log_step(AgentStep.PARSE, {"code_length": len(parsed_response.code)})
                
                # Save the generated code
                await self.common.save_code(parsed_response.code)
                
                # Create success response
                return self.common.create_success_response(
                    code=parsed_response.code,
                    thoughts=parsed_response.thoughts
                )
            except ValueError as e:
                self.common.logger.error(f"Failed to parse code: {str(e)}")
                return self.common.create_error_response(f"Failed to parse code: {str(e)}")

        except Exception as e:
            self.common.log_step(AgentStep.ERROR, {"error": str(e)}, str(e))
            return self.common.create_error_response(f"Failed to generate code: {str(e)}")

