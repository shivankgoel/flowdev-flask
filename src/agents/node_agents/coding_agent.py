import logging
from src.inference import BaseLLMInference
from src.agents.prompt_formatters.code_formatter import CodePromptFormatter
from ..models.agent_models import AgentResponse
from src.storage.models.models import CanvasDefinitionDO, CanvasDO
from src.api.models.node_models import CanvasNode
from src.agents.models.agent_models import InvokeAgentRequest
from src.api.models.dataplane_models import ProgrammingLanguage
from src.agents.llm_response_parsers.code_parser import CodeParser
from typing import List
from src.api.models.dataplane_models import CodeFile
from src.agents.models.agent_models import CodeParserResponse

logger = logging.getLogger(__name__)

class CodingAgent:
    def __init__(
        self,
        inference_client: BaseLLMInference,
        node: CanvasNode,
        canvas_definition: CanvasDefinitionDO,
        canvas: CanvasDO,
    ):
        self.inference_client = inference_client
        self.canvas = canvas
        self.canvas_definition = canvas_definition
        self.node = node
        self.code_parser = CodeParser(node_id=node.nodeId)
        self.formatter = CodePromptFormatter()
        self.logger = logger
        

    async def invoke_agent(
        self,
        invoke_agent_request: InvokeAgentRequest,
        language: ProgrammingLanguage,
        existing_code: List[CodeFile]
    ) -> AgentResponse:
        """Invoke the agent with instructions and return the response."""
        try:
            # Format prompt
            node_prompt = self.formatter.format_prompt(
                node=self.node,
                canvas_definition=self.canvas_definition,
                language=language,
                invoke_agent_request=invoke_agent_request,
                existing_code=existing_code
            )
            canvas_prompt = self.formatter.format_canvas_prompt(    
                canvas=self.canvas,
                canvas_definition=self.canvas_definition,
                language=language,
                invoke_agent_request=invoke_agent_request,
                existing_code=existing_code
            )
            node_response = await self.inference_client.generate(node_prompt)
            canvas_response = await self.inference_client.generate(canvas_prompt)
          
            # Handle different response types
            if node_response.error or canvas_response.error:
                return AgentResponse(
                    agent_node_id=self.node.nodeId,
                    code_parser_response=CodeParserResponse(addedFiles=[], updatedFiles=[], deletedFiles=[]),
                    error_message=f"Inference error: {node_response.error}"
                )

            if not node_response.text_response and not canvas_response.text_response:
                return AgentResponse(
                    agent_node_id=self.node.nodeId,
                    code_parser_response=CodeParserResponse(addedFiles=[], updatedFiles=[], deletedFiles=[]),
                    error_message="No text response received from inference"
                )

            if node_response.text_response:
                node_parser_response = self.code_parser.parse(node_response.text_response, language)
            else:
                node_parser_response = CodeParserResponse(addedFiles=[], updatedFiles=[], deletedFiles=[], reasoningSteps=[])

            if canvas_response.text_response:
                canvas_parser_response = self.code_parser.parse(canvas_response.text_response, language)
            else:
                canvas_parser_response = CodeParserResponse(addedFiles=[], updatedFiles=[], deletedFiles=[], reasoningSteps=[])

            # Parse and return the response directly
            return AgentResponse(
                agent_node_id=self.node.nodeId,
                code_parser_response=CodeParserResponse(
                    addedFiles=node_parser_response.addedFiles + canvas_parser_response.addedFiles,
                    updatedFiles=node_parser_response.updatedFiles + canvas_parser_response.updatedFiles,
                    deletedFiles=node_parser_response.deletedFiles + canvas_parser_response.deletedFiles,
                    reasoningSteps=node_parser_response.reasoningSteps + canvas_parser_response.reasoningSteps
                )
            )

        except Exception as e:
            self.logger.error(f"Error generating code: {str(e)}")
            return AgentResponse(
                agent_node_id=self.node.nodeId,
                code_parser_response=CodeParserResponse(
                    addedFiles=[],
                    updatedFiles=[],
                    deletedFiles=[],
                    reasoningSteps=[]
                ),
                error_message=f"Failed to generate code: {str(e)}"
            )

