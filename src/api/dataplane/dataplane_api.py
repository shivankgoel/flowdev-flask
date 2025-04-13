from fastapi import APIRouter, HTTPException, Request, Depends, Body
from fastapi.responses import JSONResponse, Response
from typing import Optional, Dict, Any
import logging
from dataclasses import asdict
from fastapi.exceptions import RequestValidationError

from src.api.models.dataplane_models import (
    GenerateCodeRequest,
    GenerateCodeResponse
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
        result = dataplane_handler.generate_code(customer_id, request_model)
        return handle_response(result)
    except RequestValidationError as e:
        logger.error(f"Request validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Failed to generate code")
        raise HTTPException(status_code=500, detail=f"Failed to generate code: {str(e)}")
