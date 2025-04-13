from src.agents.coordinator.agent_coordinator import AgentCoordinator
from src.storage.coordinator.canvas_coordinator import CanvasCoordinator
from src.storage.coordinator.base_coordinator import BaseCoordinator, StorageCoordinatorError
from src.api.models.dataplane_models import GenerateCodeRequest, GenerateCodeResponse, CodeFile, ProgrammingLanguage
from src.specs.flow_canvas_spec import CanvasDefinition, CanvasNodeSpec
import logging

class DataplaneCoordinator(BaseCoordinator):
    """Coordinates dataplane operations for code generation."""
    
    def __init__(self):
        super().__init__()
        self.agent_coordinator = AgentCoordinator()
        self.canvas_coordinator = CanvasCoordinator()

    async def generate_code(
        self,
        customer_id: str,
        request: GenerateCodeRequest
    ) -> GenerateCodeResponse:
        try:
            # Get canvas and node information
            canvas_do, canvas_definition = self.canvas_coordinator.get_canvas(
                customer_id,
                request.canvasId,
                request.canvasVersion
            )
            
            if not canvas_do or not canvas_definition:
                raise StorageCoordinatorError(f"Canvas not found: {request.canvasId} version {request.canvasVersion}")
            
            # Find the target node
            target_node = None
            for node in canvas_definition.nodes:
                if node.nodeId == request.nodeId:
                    target_node = node
                    break
            
            if not target_node:
                raise StorageCoordinatorError(f"Node not found: {request.nodeId}")
            
            # Generate code using agent coordinator
            response = await self.agent_coordinator.generate_code(
                node=target_node,
                canvas=canvas_definition,
                language=request.programmingLanguage,
                inference_provider="bedrock"  # Default to Bedrock for now
            )
                    
            return response
        except Exception as e:
            self.logger.error(f"Error generating code: {str(e)}")
            return {
                "error": str(e),
                "status_code": 500
            }
