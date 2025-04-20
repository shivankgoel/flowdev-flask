import logging
from src.inference import BaseLLMInference
from src.agents.prompt_formatters.code_formatter import CodePromptFormatter
from ..models.agent_models import AgentResponse
from src.storage.models.models import CanvasDefinitionDO
from src.api.models.node_models import CanvasNode
from src.agents.models.agent_models import InvokeAgentRequest
from src.api.models.dataplane_models import ProgrammingLanguage
from src.agents.llm_response_parsers.code_parser import CodeParser
from typing import List
from src.api.models.dataplane_models import CodeFile

logger = logging.getLogger(__name__)

class CodingAgent:
    def __init__(
        self,
        inference_client: BaseLLMInference,
        node: CanvasNode,
        canvas: CanvasDefinitionDO,
    ):
        self.inference_client = inference_client
        self.canvas = canvas
        self.node = node
        self.code_parser = CodeParser(node_id=node.nodeId)
        self.formatter = CodePromptFormatter()
        self.logger = logger
        

    async def invoke_agent(
        self,
        invoke_agent_request: InvokeAgentRequest,
        language: ProgrammingLanguage,
        previous_code: List[CodeFile]
    ) -> AgentResponse:
        """Invoke the agent with instructions and return the response."""
        try:
            # Format prompt
            prompt = self.formatter.format_prompt(
                node=self.node,
                canvas=self.canvas,
                language=language,
                invoke_agent_request=invoke_agent_request,
                previous_code=previous_code
            )
            response = await self.inference_client.generate(prompt)
          
            # Handle different response types
            if response.error:
                return AgentResponse(
                    agent_node_id=self.node.nodeId,
                    code="",
                    error=f"Inference error: {response.error}"
                )

            if not response.text_response:
                return AgentResponse(
                    agent_node_id=self.node.nodeId,
                    code="",
                    error="No text response received from inference"
                )

            # Print raw LLM response for debugging
            print("\n=== Raw LLM Response ===")
            print(response.text_response)
            print("=======================\n")

            # Parse and return the response directly
            return AgentResponse(
                agent_node_id=self.node.nodeId,
                code_parser_response=self.code_parser.parse(response.text_response, language)
            )

        except Exception as e:
            self.logger.error(f"Error generating code: {str(e)}")
            return AgentResponse(
                agent_node_id=self.node.nodeId,
                code="",
                error=f"Failed to generate code: {str(e)}"
            )

