from typing import Any
from src.inference.openai_inference import OpenAIInference
from src.inference.bedrock_inference import BedrockInference
from src.storage.coordinator.base_coordinator import StorageCoordinatorError
from src.api.models.node_models import CanvasNode
from src.api.models.dataplane_models import ProgrammingLanguage
from src.agents.node_agents.coding_agent import CodingAgent
from src.storage.models.models import CanvasDefinitionDO
from src.agents.models.agent_models import InvokeAgentRequest, InvokeAgentQuerySource
from src.api.models.dataplane_models import CodeFile
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from typing import List
import logging

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AgentCoordinatorGenerateCodeResponse:
    files: List[CodeFile]
    deletedFiles: List[CodeFile]

class AgentCoordinator:
    """Coordinates agent operations for different node types."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _get_inference_client(self, provider: str = "bedrock"):
        """Get the appropriate inference client based on provider."""
        if provider == "openai":
            return OpenAIInference()
        return BedrockInference()

  
    async def generate_code(
        self,
        node: CanvasNode,
        canvas: CanvasDefinitionDO,
        language: ProgrammingLanguage,
        previous_code: List[CodeFile],
        inference_provider: str = "bedrock"
    ) -> AgentCoordinatorGenerateCodeResponse:
        try:
            agent = CodingAgent (
                inference_client=self._get_inference_client(inference_provider),
                node=node,
                canvas=canvas
            )

            response = await agent.invoke_agent (
                invoke_agent_request=InvokeAgentRequest(
                    query="Generate code for the node",
                    query_source=InvokeAgentQuerySource.USER
                ),
                language=language,
                previous_code=previous_code
            )

            return AgentCoordinatorGenerateCodeResponse (
                files=response.code_parser_response.files,
                deletedFiles=[]
            )

        except Exception as e:
            self.logger.error(f"Error generating code: {str(e)}")
            raise StorageCoordinatorError(f"Failed to generate code: {str(e)}") 