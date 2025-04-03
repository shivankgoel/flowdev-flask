import logging
import json
from typing import Dict, Any, Optional, List, Callable, Awaitable
from datetime import datetime
from src.inference import BaseLLMInference
from src.inference.models.inference_models import InferenceResponse, ToolCall
from src.agents_core.agents.models.agent_models import AgentStep, AgentResponse, AgentThoughts
from src.specs.flow_canvas_spec import CanvasDefinitionSpec, ChatMessage, MessageContent, MessageContentType, ChatMessageRole
from src.agents_core.tools.common import FetchCodeTool
from src.agents_core.storage.s3_dao import S3DAO

logger = logging.getLogger(__name__)

class AgentCommon:
    """Common functionality shared by all agents."""
    
    def __init__(
        self,
        inference_client: BaseLLMInference,
        current_node_id: str,
        canvas: CanvasDefinitionSpec
    ):
        self.inference_client = inference_client
        self.current_node_id = current_node_id
        self.canvas = canvas
        self.s3_dao = S3DAO()
        self.logger = logger
        self.tool_handlers = {}
        
        # Initialize common tools
        self._init_common_tools()
        
    def _init_common_tools(self):
        """Initialize common tools with handlers."""
        # These will be set by the agent
        self.send_message_handler = None
        
        
        self.register_tool_handler("fetch_node_code", FetchCodeTool(
            canvas=self.canvas,
            current_node_id=self.current_node_id,
            s3_dao=self.s3_dao
        ))
        
    def set_handlers(self, send_message_handler):
        """Set the handlers for common tools."""
        self.send_message_handler = send_message_handler
        
        # Re-register tools with updated handlers
        self._init_common_tools()

    async def _send_message_handler(self, target_node_id: str, message: str, source_node_id: str) -> AgentResponse:
        """Handler for sending messages between agents."""
        if not self.send_message_handler:
            return self.create_error_response("Send message handler not set")
        return await self.send_message_handler(target_node_id, message, source_node_id)

    def register_tool_handler(self, tool_name: str, handler: Callable[[Dict[str, Any]], Awaitable[AgentResponse]]) -> None:
        """Register a handler for a specific tool."""
        self.tool_handlers[tool_name] = handler

    def log_step(self, step: AgentStep, details: Dict[str, Any], error: Optional[str] = None) -> None:
        """Log an agent step with details."""
        if error:
            self.logger.error(f"{step.value}: {error}", extra=details)
        else:
            self.logger.info(step.value, extra=details)

    async def save_code(self, code: str) -> str:
        """Save code to S3."""
        return self.s3_dao.save_code(
            code=code,
            customer_id=self.canvas.customer_id,
            canvas_id=self.canvas.canvas_id,
            canvas_version=self.canvas.canvas_version,
            node_id=self.current_node_id,
            language=self.canvas.programming_language.value
        )

    async def save_message(self, target_node_id: str, message: str, response: Optional[str] = None) -> None:
        """Save a message to S3."""
        # Create message content
        message_content = MessageContent(
            role=ChatMessageRole.USER,
            content_type=MessageContentType.TEXT,
            text=message
        )
        
        # Create node message
        node_message = ChatMessage(
            sender=self.current_node_id,
            timestamp=datetime.now().isoformat(),
            message_type="communication",
            contents=[message_content]
        )
        
        # Save the message
        self.s3_dao.save_message(
            customer_id=self.canvas.customer_id,
            canvas_id=self.canvas.canvas_id,
            canvas_version=self.canvas.canvas_version,
            node_id=target_node_id,
            message=node_message
        )
        
        # If there's a response, save it as a separate message
        if response:
            response_content = MessageContent(
                role=ChatMessageRole.ASSISTANT,
                content_type=MessageContentType.TEXT,
                node_assistant_id=target_node_id,
                text=response
            )
            
            response_message = ChatMessage(
                sender=target_node_id,
                timestamp=datetime.now().isoformat(),
                message_type="response",
                contents=[response_content]
            )
            
            self.s3_dao.save_message(
                customer_id=self.canvas.customer_id,
                canvas_id=self.canvas.canvas_id,
                canvas_version=self.canvas.canvas_version,
                node_id=target_node_id,
                message=response_message
            )

    def create_error_response(self, error: str) -> AgentResponse:
        """Create an error response."""
        return AgentResponse(
            agent_node_id=self.current_node_id,
            code="",
            error=error
        )

    def create_success_response(self, code: str, thoughts: Optional[str] = None) -> AgentResponse:
        """Create a success response."""
        return AgentResponse(
            agent_node_id=self.current_node_id,
            code=code,
            thoughts=AgentThoughts(thoughts=thoughts) if thoughts else None
        )

    async def handle_tool_calls(self, tool_calls: list[ToolCall]) -> list[AgentResponse]:
        """Handle tool calls using registered handlers."""
        responses = []
        
        for tool_call in tool_calls:
            if tool_call.name in self.tool_handlers:
                try:
                    response = await self.tool_handlers[tool_call.name](tool_call.arguments)
                    responses.append(response)
                except Exception as e:
                    self.logger.error(f"Error handling tool call {tool_call.name}: {str(e)}")
                    responses.append(self.create_error_response(f"Error handling tool call {tool_call.name}: {str(e)}"))
            else:
                responses.append(self.create_error_response(f"Unsupported tool call: {tool_call.name}"))
                
        return responses 