from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
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

router = APIRouter()
canvas_handler = CanvasApiHandler()

def handle_response(result):
    if "error" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])
    return JSONResponse(content=result.get("data", {}), status_code=result["status_code"])

@router.post('/api/v1/canvas', response_model=CreateCanvasResponse)
async def create_canvas(
    request_model: CreateCanvasRequest,
    request: Request,
    customer_id: str = Depends(CognitoAuth.require_auth)
):
    """Create a new canvas with the given name and optional metadata."""
    try:
        result = canvas_handler.create_canvas(customer_id, request_model)
        return handle_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create canvas: {str(e)}")

@router.get('/api/v1/canvas', response_model=ListCanvasResponse)
async def list_canvases(
    request: Request,
    customer_id: str = Depends(CognitoAuth.require_auth)
):
    """List all canvases for the current customer."""
    try:
        request_model = ListCanvasRequest()
        result = canvas_handler.list_canvases(customer_id, request_model)
        return handle_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list canvases: {str(e)}")

@router.get('/api/v1/canvas/{canvas_id}', response_model=GetCanvasResponse)
async def get_canvas(
    canvas_id: str,
    version: Optional[str] = 'latest',
    request: Request = None,
    customer_id: str = Depends(CognitoAuth.require_auth)
):
    """Get a specific canvas by ID and optional version."""
    try:
        request_model = GetCanvasRequest(canvas_id=canvas_id, canvas_version=version)
        result = canvas_handler.get_canvas(customer_id, request_model)
        return handle_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get canvas: {str(e)}")

@router.put('/api/v1/canvas/{canvas_id}', response_model=UpdateCanvasResponse)
async def update_canvas(
    canvas_id: str,
    request_model: UpdateCanvasRequest,
    request: Request,
    customer_id: str = Depends(CognitoAuth.require_auth)
):
    """Update the draft version of a canvas with new name, description, or metadata."""
    try:
        result = canvas_handler.update_canvas(customer_id, request_model)
        return handle_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update canvas: {str(e)}")

@router.delete('/api/v1/canvas/{canvas_id}', response_model=DeleteCanvasResponse)
async def delete_canvas(
    canvas_id: str,
    version: Optional[str] = 'latest',
    request: Request = None,
    customer_id: str = Depends(CognitoAuth.require_auth)
):
    """Delete a specific canvas version or all versions if no version specified."""
    try:
        request_model = DeleteCanvasRequest(canvas_id=canvas_id, canvas_version=version)
        result = canvas_handler.delete_canvas(customer_id, request_model)
        return handle_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete canvas: {str(e)}")

@router.get('/api/v1/canvas/{canvas_id}/versions', response_model=ListCanvasVersionsResponse)
async def list_canvas_versions(
    canvas_id: str,
    request: Request,
    customer_id: str = Depends(CognitoAuth.require_auth)
):
    """List all versions of a specific canvas."""
    try:
        request_model = ListCanvasVersionsRequest(canvas_id=canvas_id)
        result = canvas_handler.list_canvas_versions(customer_id, request_model)
        return handle_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list canvas versions: {str(e)}")

@router.post('/api/v1/canvas/{canvas_id}/version', response_model=CreateCanvasVersionResponse)
async def create_canvas_version(
    canvas_id: str,
    request: Request,
    customer_id: str = Depends(CognitoAuth.require_auth)
):
    """Create a new version of a canvas from the current draft."""
    try:
        request_model = CreateCanvasVersionRequest(canvas_id=canvas_id)
        result = canvas_handler.create_canvas_version(customer_id, request_model)
        return handle_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create new version: {str(e)}") 