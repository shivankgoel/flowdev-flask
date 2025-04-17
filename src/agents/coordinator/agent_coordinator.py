from typing import Dict, Any
from src.inference.openai_inference import OpenAIInference
from src.inference.bedrock_inference import BedrockInference
from src.storage.coordinator.base_coordinator import StorageCoordinatorError
from src.api.models.node_models import CanvasNode, CanvasNodeType
from src.api.models.dataplane_models import ProgrammingLanguage
from src.agents.node_agents.coding_agent import CodingAgent
from src.storage.models.models import CanvasDefinitionDO
from src.agents.models.agent_models import InvokeAgentRequest, InvokeAgentQuerySource
from src.api.models.dataplane_models import GenerateCodeResponse
import logging

class AgentCoordinator:
    """Coordinates agent operations for different node types."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _get_inference_client(self, provider: str = "bedrock"):
        """Get the appropriate inference client based on provider."""
        if provider == "openai":
            return OpenAIInference()
        return BedrockInference()

    def get_agent_based_on_node_type(self, inference_provider: str, node: CanvasNode, canvas: CanvasDefinitionDO) -> Any:
        return CodingAgent(
            inference_client=self._get_inference_client(),
            node=node,
            canvas=canvas
        )

    async def generate_code(
        self,
        node: CanvasNode,
        canvas: CanvasDefinitionDO,
        language: ProgrammingLanguage,
        inference_provider: str = "bedrock"
    ) -> Dict[str, Any]:
        try:
            agent = self.get_agent_based_on_node_type(inference_provider, node, canvas)

            response = await agent.invoke_agent(
                invoke_agent_request=InvokeAgentRequest(
                    query="Generate code for the node",
                    query_source=InvokeAgentQuerySource.USER
                ),
                language=language,
                previous_code=""
            )

            return GenerateCodeResponse(
                files=response.code_parser_response.files
            )

        except Exception as e:
            self.logger.error(f"Error generating code: {str(e)}")
            raise StorageCoordinatorError(f"Failed to generate code: {str(e)}") 