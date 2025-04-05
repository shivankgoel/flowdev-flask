from fastapi import APIRouter, HTTPException, Request, Depends, Body
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import traceback

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
    return JSONResponse(content=result.get("data", {}), status_code=result.get("status_code", 200))

# Canvas Collection Operations
@router.post('', response_model=CreateCanvasResponse)
async def create_canvas(
    request_model: CreateCanvasRequest = Body(...),
    request: Request = None,
    customer_id: str = Depends(CognitoAuth.get_customer_id)
):
    """Create a new canvas with the given name and optional metadata."""
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
    """Get a specific canvas by ID and version."""
    try:
        request_model = GetCanvasRequest(canvas_id=canvas_id, canvas_version=version)
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
    """Update the draft version of a canvas with new name, description, or metadata."""
    try:
        result = canvas_handler.update_canvas(customer_id, request_model)
        return handle_response(result)
    except Exception as e:
        logger.exception("Failed to update canvas")
        raise HTTPException(status_code=500, detail=f"Failed to update canvas: {str(e)}")

@router.delete('/{canvas_id}', response_model=DeleteCanvasResponse)
async def delete_canvas(
    canvas_id: str,
    request: Request = None,
    customer_id: str = Depends(CognitoAuth.get_customer_id)
):
    """Delete a canvas and all its versions."""
    try:
        request_model = DeleteCanvasRequest(canvas_id=canvas_id)
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
        request_model = ListCanvasVersionsRequest(canvas_id=canvas_id)
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
    """Create a new version of a canvas from the current draft."""
    try:
        request_model = CreateCanvasVersionRequest(canvas_id=canvas_id)
        result = canvas_handler.create_canvas_version(customer_id, request_model)
        return handle_response(result)
    except Exception as e:
        logger.exception("Failed to create canvas version")
        raise HTTPException(status_code=500, detail=f"Failed to create new version: {str(e)}")
