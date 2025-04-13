from fastapi import APIRouter, HTTPException, Request, Depends, Body
from fastapi.responses import JSONResponse, Response
from typing import Optional, Dict, Any
import logging
from dataclasses import asdict
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.api.models.canvas_models import (
    CreateCanvasRequest,
    UpdateCanvasRequest,
    GetCanvasRequest,
    DeleteCanvasRequest,
    CreateCanvasVersionRequest,
    ListCanvasVersionsRequest,
    ListCanvasRequest,
    ListCanvasResponse,
    ListCanvasVersionsResponse,
    CreateCanvasResponse,
    UpdateCanvasResponse,
    DeleteCanvasResponse,
    GetCanvasResponse,
    CreateCanvasVersionResponse
)
from src.api.handlers.canvas_handler import CanvasApiHandler
from src.api.auth.cognito_auth import CognitoAuth

router = APIRouter(prefix="/api/v1/canvas")
canvas_handler = CanvasApiHandler()
logger = logging.getLogger(__name__)

def handle_response(result: Dict[str, Any]) -> Response:
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result["error"])
    
    # Convert the result to a dictionary if it's a dataclass
    data = result.get("data", {})
    if hasattr(data, '__dataclass_fields__'):
        data = asdict(data)
    
    # Handle CanvasNode objects in the response
    def serialize_node(node):
        if hasattr(node, 'to_dict'):
            return node.to_dict()
        return node
    
    # Recursively serialize any CanvasNode objects in the response
    def serialize_data(obj):
        if isinstance(obj, list):
            return [serialize_data(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: serialize_data(v) for k, v in obj.items()}
        else:
            return serialize_node(obj)
    
    serialized_data = serialize_data(data)
    return JSONResponse(
        content=serialized_data,
        status_code=result.get("status_code", 200),
        media_type="application/json"
    )

# Canvas Collection Operations
@router.post('', response_model=CreateCanvasResponse)
async def create_canvas(
    request_model: CreateCanvasRequest = Body(...),
    request: Request = None,
    customer_id: str = Depends(CognitoAuth.get_customer_id)
):
    """Create a new canvas with the given name and optional canvas definition."""
    try:
        result = canvas_handler.create_canvas(customer_id, request_model)
        return handle_response(result)
    except Exception as e:
        logger.exception("Failed to create canvas")
        raise HTTPException(status_code=500, detail=f"Failed to create canvas: {str(e)}")

@router.get('', response_model=ListCanvasResponse)
async def list_canvases(
    request: Request = None,
    customer_id: str = Depends(CognitoAuth.get_customer_id)
):
    """List all canvases for the current customer."""
    try:
        request_model = ListCanvasRequest()
        result = canvas_handler.list_canvases(customer_id, request_model)
        return handle_response(result)
    except Exception as e:
        logger.exception("Failed to list canvases")
        raise HTTPException(status_code=500, detail=f"Failed to list canvases: {str(e)}")

# Individual Canvas Operations
@router.get('/{canvas_id}', response_model=GetCanvasResponse)
async def get_canvas(
    canvas_id: str,
    version: Optional[str] = 'draft',
    request: Request = None,
    customer_id: str = Depends(CognitoAuth.get_customer_id)
):
    """Get a specific canvas by ID and version, including its definition if available."""
    try:
        request_model = GetCanvasRequest(canvasId=canvas_id, canvasVersion=version)
        result = canvas_handler.get_canvas(customer_id, request_model)
        return handle_response(result)
    except Exception as e:
        logger.exception("Failed to get canvas")
        raise HTTPException(status_code=500, detail=f"Failed to get canvas: {str(e)}")

@router.put('', response_model=UpdateCanvasResponse)
async def update_canvas(
    request_model: UpdateCanvasRequest = Body(...),
    request: Request = None,
    customer_id: str = Depends(CognitoAuth.get_customer_id)
):
    """Update the draft version of a canvas with new name and/or canvas definition."""
    try:
        # Log the raw request body
        body = await request.body()
        logger.info(f"Raw request body: {body.decode()}")
        
        # Log the parsed request model
        logger.info(f"Parsed request model: {request_model}")
        logger.info(f"Canvas ID: {request_model.canvasId}")
        logger.info(f"Canvas Name: {request_model.canvasName}")
        logger.info(f"Nodes count: {len(request_model.nodes) if request_model.nodes else 0}")
        logger.info(f"Edges count: {len(request_model.edges) if request_model.edges else 0}")
        
        result = canvas_handler.update_canvas(customer_id, request_model)
        return handle_response(result)
    except RequestValidationError as e:
        logger.error(f"Request validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Failed to update canvas")
        raise HTTPException(status_code=500, detail=f"Failed to update canvas: {str(e)}")

@router.delete('/{canvas_id}', response_model=DeleteCanvasResponse)
async def delete_canvas(
    canvas_id: str,
    request: Request = None,
    customer_id: str = Depends(CognitoAuth.get_customer_id)
):
    """Delete a canvas and all its versions, including their definitions in S3."""
    try:
        request_model = DeleteCanvasRequest(canvasId=canvas_id)
        result = canvas_handler.delete_canvas(customer_id, request_model)
        return handle_response(result)
    except Exception as e:
        logger.exception("Failed to delete canvas")
        raise HTTPException(status_code=500, detail=f"Failed to delete canvas: {str(e)}")

# Canvas Version Operations
@router.get('/{canvas_id}/versions', response_model=ListCanvasVersionsResponse)
async def list_canvas_versions(
    canvas_id: str,
    request: Request = None,
    customer_id: str = Depends(CognitoAuth.get_customer_id)
):
    """List all versions of a specific canvas."""
    try:
        request_model = ListCanvasVersionsRequest(canvasId=canvas_id)
        result = canvas_handler.list_canvas_versions(customer_id, request_model)
        return handle_response(result)
    except Exception as e:
        logger.exception("Failed to list canvas versions")
        raise HTTPException(status_code=500, detail=f"Failed to list canvas versions: {str(e)}")

@router.post('/{canvas_id}/version', response_model=CreateCanvasVersionResponse)
async def create_canvas_version(
    canvas_id: str,
    request: Request = None,
    customer_id: str = Depends(CognitoAuth.get_customer_id)
):
    """Create a new version of a canvas from the current draft, including its definition."""
    try:
        request_model = CreateCanvasVersionRequest(canvasId=canvas_id)
        result = canvas_handler.create_canvas_version(customer_id, request_model)
        return handle_response(result)
    except Exception as e:
        logger.exception("Failed to create canvas version")
        raise HTTPException(status_code=500, detail=f"Failed to create new version: {str(e)}")
