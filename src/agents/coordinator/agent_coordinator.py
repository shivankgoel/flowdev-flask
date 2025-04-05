from typing import Dict, Any, Optional
from src.agents_core.agents.dynamodb_agent import DynamoDBAgent
from src.inference.openai_inference import OpenAIInference
from src.inference.bedrock_inference import BedrockInference
from src.specs.flow_canvas_spec import CanvasDefinition, CanvasNodeSpec
from .base_coordinator import StorageCoordinatorError
import logging

class AgentCoordinator:
    """Coordinates agent operations for different node types."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._agent_registry = {
            "dynamodb": DynamoDBAgent
            # Add more agents here as they are implemented
        }

    def _get_inference_client(self, provider: str = "bedrock"):
        """Get the appropriate inference client based on provider."""
        if provider == "openai":
            return OpenAIInference()
        return BedrockInference()

    def _create_minimal_canvas(
        self,
        customer_id: str,
        canvas_id: str,
        canvas_version: str,
        node: CanvasNodeSpec
    ) -> CanvasDefinition:
        """Create a minimal canvas definition for the agent."""
        return CanvasDefinition(
            customer_id=customer_id,
            canvas_id=canvas_id,
            canvas_version=canvas_version,
            nodes=[node],
            edges=[],
            created_at=node.metadata.get("created_at", ""),
            updated_at=node.metadata.get("updated_at", "")
        )

    async def generate_code(
        self,
        node: CanvasNodeSpec,
        customer_id: str,
        canvas_id: str,
        canvas_version: str,
        language: str,
        inference_provider: str = "bedrock"
    ) -> Dict[str, Any]:
        """Generate code for a node using the appropriate agent.
        
        Args:
            node: The node to generate code for
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            language: Programming language to generate code in
            inference_provider: LLM provider to use ("bedrock" or "openai")
            
        Returns:
            Dict[str, Any]: Generated code and metadata
            
        Raises:
            StorageCoordinatorError: If code generation fails
        """
        try:
            # Get the appropriate agent class
            agent_class = self._agent_registry.get(node.type)
            if not agent_class:
                raise StorageCoordinatorError(f"Unsupported node type: {node.type}")

            # Initialize inference client
            inference_client = self._get_inference_client(inference_provider)

            # Create minimal canvas
            canvas = self._create_minimal_canvas(
                customer_id=customer_id,
                canvas_id=canvas_id,
                canvas_version=canvas_version,
                node=node
            )

            # Initialize agent
            agent = agent_class(
                inference_client=inference_client,
                current_node_id=node.id,
                canvas=canvas,
                send_message_handler=lambda *args, **kwargs: None
            )

            # Generate code
            response = await agent.invoke_agent()
            if response.error:
                raise StorageCoordinatorError(f"Code generation failed: {response.error}")

            return {
                "code": response.code,
                "language": language,
                "node_id": node.id,
                "thoughts": response.thoughts
            }

        except Exception as e:
            self.logger.error(f"Error generating code: {str(e)}")
            raise StorageCoordinatorError(f"Failed to generate code: {str(e)}") 