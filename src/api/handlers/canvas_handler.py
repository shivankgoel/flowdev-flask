from typing import Dict, Any, Optional
from datetime import datetime
import uuid
from src.storage.coordinator.canvas_coordinator import CanvasCoordinator
from src.storage.models.models import CanvasDO, CanvasDefinitionDO
from src.api.models.canvas_models import (
    CreateCanvasRequest,
    CreateCanvasResponse,
    UpdateCanvasRequest,
    UpdateCanvasResponse,
    GetCanvasRequest,
    GetCanvasResponse,
    DeleteCanvasRequest,
    DeleteCanvasResponse,
    ListCanvasVersionsRequest,
    ListCanvasVersionsResponse,
    ListCanvasVersionsResponseItem,
    CreateCanvasVersionRequest,
    CreateCanvasVersionResponse,
    ListCanvasRequest,
    ListCanvasResponse,
    ListCanvasResponseItem
)

class CanvasApiHandler:
    def __init__(self):
        self.coordinator = CanvasCoordinator()
    
    def create_canvas(self, customer_id: str, request: CreateCanvasRequest) -> Dict[str, Any]:
        try:
            canvas_id = str(uuid.uuid4())
            canvas_version = "draft"
            timestamp = datetime.utcnow().isoformat()
            
            canvas_do = CanvasDO(
                canvas_name=request.canvasName,
                customer_id=customer_id,
                canvas_id=canvas_id,
                canvas_version=canvas_version,
                created_at=timestamp,
                updated_at=timestamp,
                canvas_definition_s3_uri=None
            )
            
            # Create canvas definition if provided
            canvas_definition = None
            if hasattr(request, 'nodes') and hasattr(request, 'edges'):
                canvas_definition = CanvasDefinitionDO(
                    nodes=request.nodes,
                    edges=request.edges
                )
            

            success = self.coordinator.save_canvas(canvas_do, canvas_definition)
            if success:
                response = CreateCanvasResponse(canvasId=canvas_id)
                return {"data": response.__dict__, "status_code": 201}
            return {"error": "Failed to create canvas", "status_code": 500}
        except Exception as e:
            import traceback
            return {"error": f"Failed to create canvas: {str(e)}", "status_code": 500}
    
    def get_canvas(self, customer_id: str, request: GetCanvasRequest) -> Dict[str, Any]:
        try:
            canvas, definition = self.coordinator.get_canvas(
                customer_id, 
                request.canvasId, 
                request.canvasVersion
            )
            if not canvas:
                return {"error": "Canvas not found", "status_code": 404}
            
            response = GetCanvasResponse(
                canvasId=canvas.canvas_id,
                canvasVersion=canvas.canvas_version,
                canvasName=canvas.canvas_name,
                createdAt=canvas.created_at,
                updatedAt=canvas.updated_at,
                nodes=definition.nodes if definition else None,
                edges=definition.edges if definition else None
            )
            return {"data": response.__dict__, "status_code": 200}
        except Exception as e:
            return {"error": f"Failed to get canvas: {str(e)}", "status_code": 500}
    
    def update_canvas(self, customer_id: str, request: UpdateCanvasRequest) -> Dict[str, Any]:
        try:
            canvas, definition = self.coordinator.get_canvas(
                customer_id, 
                request.canvasId, 
                "draft"
            )
            if not canvas:
                return {"error": "Canvas not found", "status_code": 404}
            
            canvas.canvas_name = request.canvasName
            canvas.updated_at = datetime.utcnow().isoformat()

            if hasattr(request, 'nodes') and hasattr(request, 'edges'):
                definition = CanvasDefinitionDO(
                    nodes=request.nodes,
                    edges=request.edges
                )

            success = self.coordinator.save_canvas(canvas, definition)
            if success:
                response = UpdateCanvasResponse(canvasId=canvas.canvas_id)
                return {"data": response.__dict__, "status_code": 200}
            return {"error": "Failed to update canvas", "status_code": 500}
        except Exception as e:
            return {"error": f"Failed to update canvas: {str(e)}", "status_code": 500}
    
    def delete_canvas(self, customer_id: str, request: DeleteCanvasRequest) -> Dict[str, Any]:
        try:
            if self.coordinator.delete_canvas_all_versions(customer_id, request.canvasId):
                response = DeleteCanvasResponse(canvasId=request.canvasId)
                return {"data": response.__dict__, "status_code": 200}
            return {"error": "Failed to delete canvas", "status_code": 500}
        except Exception as e:
            return {"error": f"Failed to delete canvas: {str(e)}", "status_code": 500}
    
    def list_canvas_versions(self, customer_id: str, request: ListCanvasVersionsRequest) -> Dict[str, Any]:
        try:
            versions = self.coordinator.list_canvas_versions(customer_id, request.canvasId)
            response = ListCanvasVersionsResponse(
                canvasVersions=[
                    ListCanvasVersionsResponseItem(
                        canvasId=request.canvasId,
                        canvasVersion=version
                    ) for version in versions
                ]
            )
            return {"data": response.to_dict(), "status_code": 200}
        except Exception as e:
            return {"error": f"Failed to list canvas versions: {str(e)}", "status_code": 500}
    
    def create_canvas_version(self, customer_id: str, request: CreateCanvasVersionRequest) -> Dict[str, Any]:
        try:
            new_version = self.coordinator.create_canvas_version(customer_id, request.canvasId)
            if new_version:
                response = CreateCanvasVersionResponse(
                    canvasId=request.canvasId,
                    canvasVersion=new_version
                )
                return {"data": response.__dict__, "status_code": 201}
            return {"error": "Failed to create new version", "status_code": 500}
        except Exception as e:
            return {"error": f"Failed to create new version: {str(e)}", "status_code": 500}
    
    def list_canvases(self, customer_id: str, request: ListCanvasRequest) -> Dict[str, Any]:
        try:
            canvases = self.coordinator.get_unique_canvases(customer_id)
            response = ListCanvasResponse(
                canvases=[
                    ListCanvasResponseItem(
                        canvasId=canvas.canvas_id,
                        canvasName=canvas.canvas_name,
                        canvasVersion=canvas.canvas_version,
                        createdAt=canvas.created_at,
                        updatedAt=canvas.updated_at
                    ) for canvas in canvases
                ]
            )
            return {"data": response.to_dict(), "status_code": 200}
        except Exception as e:
            return {"error": f"Failed to list canvases: {str(e)}", "status_code": 500} 