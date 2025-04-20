from fastapi import APIRouter, HTTPException, Request, Depends, Body
from fastapi.responses import JSONResponse, Response
from typing import Optional, Dict, Any
import logging
from dataclasses import asdict
from fastapi.exceptions import RequestValidationError
from src.api.models.dataplane_models import CodeChange


from src.api.models.dataplane_models import (
    GenerateCodeRequest,
    GenerateCodeResponse,
    ApplyCodeChangesRequest,
    ApplyCodeChangesResponse,
    GetCodeRequest,
    GetCodeResponse,
    CodeFile
)
from src.api.handlers.dataplane_handler import DataplaneApiHandler
from src.api.auth.cognito_auth import CognitoAuth

router = APIRouter(prefix="/api/v1/dataplane", tags=["dataplane"])
dataplane_handler = DataplaneApiHandler()
logger = logging.getLogger(__name__)

def handle_response(result: Dict[str, Any]) -> Response:
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result["error"])
    
    # Convert the result to a dictionary if it's a dataclass
    data = result.get("data", {})
    if hasattr(data, '__dataclass_fields__'):
        data = asdict(data)
    
    return JSONResponse(
        content=data,
        status_code=result.get("status_code", 200),
        media_type="application/json"
    )

@router.post('/generate-code', response_model=GenerateCodeResponse)
async def generate_code(
    request_model: GenerateCodeRequest = Body(...),
    request: Request = None,
    customer_id: str = Depends(CognitoAuth.get_customer_id)
):
    """Generate code for a specific node in a canvas."""
    try:
        result = await dataplane_handler.generate_code(customer_id, request_model)
        return result
    except RequestValidationError as e:
        logger.error(f"Request validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Failed to generate code")
        raise HTTPException(status_code=500, detail=f"Failed to generate code: {str(e)}")

def deserialize_codefile_list(lst):
    return [CodeFile.from_dict(f) if isinstance(f, dict) else f for f in lst or []]

@router.post('/apply-code-changes', response_model=ApplyCodeChangesResponse)
async def apply_code_changes(
    request_model: ApplyCodeChangesRequest = Body(...),
    request: Request = None,
    customer_id: str = Depends(CognitoAuth.get_customer_id)
):
    """Apply code changes to a specific node in a canvas."""        
    try:
        logger.info(f"Applying code changes for customer {customer_id} with request {request_model}")

        if isinstance(request_model.codeChange, dict):
            request_model.codeChange = CodeChange.from_dict(request_model.codeChange)

        # Ensure nested fields are deserialized
        request_model.codeChange.addedFiles = deserialize_codefile_list(request_model.codeChange.addedFiles)
        request_model.codeChange.updatedFiles = deserialize_codefile_list(request_model.codeChange.updatedFiles)
        request_model.codeChange.deletedFiles = deserialize_codefile_list(request_model.codeChange.deletedFiles)

        result = await dataplane_handler.apply_code_changes(customer_id, request_model)
        return ApplyCodeChangesResponse(success=True)

    except RequestValidationError as e:
        logger.error(f"Request validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e)) 

    except Exception as e:
        logger.exception("Failed to apply code changes")
        raise HTTPException(status_code=500, detail=f"Failed to apply code changes: {str(e)}")

@router.post('/get-code', response_model=GetCodeResponse)
async def get_code(
    request_model: GetCodeRequest = Body(...),
    request: Request = None,
    customer_id: str = Depends(CognitoAuth.get_customer_id)
):
    """Get code for a specific node in a canvas."""
    try:
        result = await dataplane_handler.get_code(customer_id, request_model)
        return result
    except RequestValidationError as e:
        logger.error(f"Request validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Failed to get code")
        raise HTTPException(status_code=500, detail=f"Failed to get code: {str(e)}")