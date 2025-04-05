from typing import Dict, Any, Optional
from datetime import datetime
import uuid
from src.storage.coordinator.canvas_coordinator import CanvasCoordinator
from src.storage.models.models import CanvasDO
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
            print(f"Creating canvas with name: {request.canvas_name}, id: {canvas_id}")
            canvas_do = CanvasDO(
                canvas_name=request.canvas_name,
                customer_id=customer_id,
                canvas_id=canvas_id,
                canvas_version=canvas_version,
                created_at=timestamp,
                updated_at=timestamp
            )
            print(f"Canvas DO created: {canvas_do}")
            success = self.coordinator.save_canvas(canvas_do)
            print(f"Save result: {success}")
            if success:
                response = CreateCanvasResponse(canvas_id=canvas_id)
                return {"data": response.__dict__, "status_code": 201}
            return {"error": "Failed to create canvas", "status_code": 500}
        except Exception as e:
            print(f"Error creating canvas: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return {"error": f"Failed to create canvas: {str(e)}", "status_code": 500}
    
    def get_canvas(self, customer_id: str, request: GetCanvasRequest) -> Dict[str, Any]:
        try:
            canvas = self.coordinator.get_canvas(
                customer_id, 
                request.canvas_id, 
                request.canvas_version
            )
            if not canvas:
                return {"error": "Canvas not found", "status_code": 404}
            response = GetCanvasResponse(
                canvas_id=canvas.canvas_id,
                canvas_version=canvas.canvas_version,
                canvas_name=canvas.canvas_name,
                created_at=canvas.created_at,
                updated_at=canvas.updated_at
            )
            return {"data": response.__dict__, "status_code": 200}
        except Exception as e:
            return {"error": f"Failed to get canvas: {str(e)}", "status_code": 500}
    
    def update_canvas(self, customer_id: str, request: UpdateCanvasRequest) -> Dict[str, Any]:
        try:
            canvas = self.coordinator.get_canvas(
                customer_id, 
                request.canvas_id, 
                "draft"
            )
            if not canvas:
                return {"error": "Canvas not found", "status_code": 404}
            canvas_do = CanvasDO(
                canvas_name=request.canvas_name,
                customer_id=customer_id,
                canvas_id=request.canvas_id,
                canvas_version="draft",
                created_at=canvas.created_at,
                updated_at=datetime.utcnow().isoformat() 
            )
            if self.coordinator.save_canvas(canvas_do):
                response = UpdateCanvasResponse(canvas_id=request.canvas_id)
                return {"data": response.to_dict(), "status_code": 200}
            return {"error": "Failed to update canvas", "status_code": 500}
        except Exception as e:
            return {"error": f"Failed to update canvas: {str(e)}", "status_code": 500}
    
    def delete_canvas(self, customer_id: str, request: DeleteCanvasRequest) -> Dict[str, Any]:
        try:
            if self.coordinator.delete_canvas_all_versions(customer_id, request.canvas_id):
                response = DeleteCanvasResponse(canvas_id=request.canvas_id)
                return {"data": response.__dict__, "status_code": 200}
            return {"error": "Failed to delete canvas", "status_code": 500}
        except Exception as e:
            return {"error": f"Failed to delete canvas: {str(e)}", "status_code": 500}
    
    def list_canvas_versions(self, customer_id: str, request: ListCanvasVersionsRequest) -> Dict[str, Any]:
        try:
            versions = self.coordinator.list_canvas_versions(customer_id, request.canvas_id)
            response = ListCanvasVersionsResponse(
                canvas_versions=[
                    ListCanvasVersionsResponseItem(
                        canvas_id=request.canvas_id,
                        canvas_version=version
                    ) for version in versions
                ]
            )
            return {"data": response.to_dict(), "status_code": 200}
        except Exception as e:
            return {"error": f"Failed to list canvas versions: {str(e)}", "status_code": 500}
    
    def create_canvas_version(self, customer_id: str, request: CreateCanvasVersionRequest) -> Dict[str, Any]:
        try:
            new_version = self.coordinator.create_canvas_version(customer_id, request.canvas_id)
            if new_version:
                response = CreateCanvasVersionResponse(
                    canvas_id=request.canvas_id,
                    canvas_version=new_version
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
                        canvas_id=canvas.canvas_id,
                        canvas_name=canvas.canvas_name
                    ) for canvas in canvases
                ]
            )
            return {"data": response.to_dict(), "status_code": 200}
        except Exception as e:
            return {"error": f"Failed to list canvases: {str(e)}", "status_code": 500} 