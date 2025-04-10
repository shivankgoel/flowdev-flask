from fastapi import APIRouter, Request, HTTPException, Depends, Body
from fastapi.responses import JSONResponse
from typing import Optional, Dict
import os
from .cognito_auth import CognitoAuth
import requests
from urllib.parse import urlencode
import logging
import base64
import boto3
logger = logging.getLogger(__name__)

from src.api.models.auth_models import (
    LogoutRequest,
    LogoutResponse,
    GoogleLoginRequest,
    OAuthLoginResponse,
    GetTokenRequest,
    RefreshTokenRequest,
    OAuthTokenResponse,
    CognitoConfig
)

router = APIRouter(prefix="/auth", tags=["auth"])

def get_cognito_config() -> CognitoConfig:
    """Get Cognito configuration from environment variables
    
    Returns:
        CognitoConfig: Strongly typed Cognito configuration
    """
    return CognitoConfig(
        region=os.getenv('COGNITO_REGION', 'us-east-1'),
        user_pool_id=os.getenv('COGNITO_USER_POOL_ID'),
        app_client_id=os.getenv('COGNITO_APP_CLIENT_ID'),
        app_client_secret=os.getenv('COGNITO_APP_CLIENT_SECRET'),
        domain=os.getenv('COGNITO_DOMAIN'),
        callback_url=os.getenv('COGNITO_CALLBACK_URL')
    )

def validate_cognito_config(config: CognitoConfig) -> Optional[str]:
    """Validate Cognito configuration and return error message if invalid"""
    missing_configs = []
    if not config.user_pool_id:
        missing_configs.append("COGNITO_USER_POOL_ID")
    if not config.app_client_id:
        missing_configs.append("COGNITO_APP_CLIENT_ID")
    if not config.app_client_secret:
        missing_configs.append("COGNITO_APP_CLIENT_SECRET")
    if not config.domain:
        missing_configs.append("COGNITO_DOMAIN")
    if not config.callback_url:
        missing_configs.append("COGNITO_CALLBACK_URL")
    
    if missing_configs:
        return f"Missing Cognito configuration: {', '.join(missing_configs)}"
    return None


def create_auth_headers(config: CognitoConfig) -> Dict[str, str]:
    # Create the Authorization header with client credentials
    client_credentials = f"{config.app_client_id}:{config.app_client_secret}"
    auth_header = base64.b64encode(client_credentials.encode()).decode()
    
    return {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth_header}"
    }

async def get_validated_cognito_config() -> CognitoConfig:
    # Get Cognito configuration
    config = get_cognito_config()
    config_error = validate_cognito_config(config)
    if config_error:
        logger.error(f"Cognito configuration error: {config_error}")
        raise HTTPException(
            status_code=500,
            detail=config_error
        )
    return config

async def handle_cognito_error(
    e: Exception,
    operation: str,
    sensitive_data: bool = True
) -> None:
    """Handle Cognito API errors consistently
    
    Args:
        e: The exception that occurred
        operation: Description of the operation that failed
        sensitive_data: Whether the error might contain sensitive data
    """
    if isinstance(e, requests.exceptions.HTTPError):
        error_response = e.response.json() if e.response else {}
        error_type = error_response.get('error', 'unknown_error')
        error_description = error_response.get('error_description', str(e))
        
        logger.error(f"{operation} failed: {error_type}")
        if e.response:
            logger.error(f"Response status: {e.response.status_code}")
            if not sensitive_data:
                logger.error(f"Response body: {error_response}")
        
        raise HTTPException(
            status_code=500,
            detail=f"{operation} failed: {error_description}"
        )
    else:
        logger.error(f"Unexpected error during {operation}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during {operation}"
        )

async def exchange_token(
    config: CognitoConfig,
    data: Dict[str, str],
    operation: str = "token exchange"
) -> OAuthTokenResponse:
    """Common function to exchange tokens with Cognito
    
    Args:
        config: Cognito configuration
        data: Request data for token exchange
        operation: Description of the operation for logging
    """
    # Construct the token endpoint URL
    token_url = f"https://{config.domain}/oauth2/token"
    
    # Get headers using common function
    headers = create_auth_headers(config)
    
    try:
        # Make the request to exchange the token
        response = requests.post(token_url, headers=headers, data=data)
        
        # Log only non-sensitive response information
        logger.info(f"{operation} response status: {response.status_code}")
        logger.info(f"{operation} successful")
        
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the token response
        token_data = response.json()
        
        # Create strongly typed response
        return OAuthTokenResponse(
            access_token=token_data['access_token'],
            refresh_token=token_data.get('refresh_token'),
            id_token=token_data.get('id_token'),
            token_type=token_data['token_type'],
            expires_in=token_data['expires_in']
        )
        
    except Exception as e:
        await handle_cognito_error(e, operation, sensitive_data=True)

@router.api_route("/logout", methods=["GET", "POST"], response_model=LogoutResponse)
async def logout(
    request: Request,
    logout_request: LogoutRequest = Body(...)
) -> LogoutResponse:
    """Logout user from Cognito and clear local session"""
    # Get and validate Cognito configuration
    config = await get_validated_cognito_config()
    
    try:
        # First, revoke the refresh token
        revoke_url = f"https://{config.domain}/oauth2/revoke"
        
        # Get headers using common function
        headers = create_auth_headers(config)
        
        # Send the refresh token to revoke
        revoke_data = {
            "token": logout_request.refresh_token
        }
        
        logger.info(f"Revoke URL: {revoke_url}")
        revoke_response = requests.post(revoke_url, headers=headers, data=revoke_data)
        revoke_response.raise_for_status()
        logger.info("Refresh token successfully revoked")
        
        return LogoutResponse(
            message="Refresh token successfully revoked",
        )
        
    except Exception as e:
        await handle_cognito_error(e, "token revocation", sensitive_data=True)

@router.api_route("/google", methods=["GET", "POST"], response_model=OAuthLoginResponse)
async def google_login(request: Request, _: GoogleLoginRequest = Depends()) -> OAuthLoginResponse:
    """Initiate Google login through Cognito"""
    # Get and validate Cognito configuration
    config = await get_validated_cognito_config()
    params = {
        "identity_provider": "Google",
        "client_id": config.app_client_id,
        "response_type": "code",
        "scope": "openid email",
        "redirect_uri": config.callback_url
    }
    auth_url = f"https://{config.domain}/oauth2/authorize?{urlencode(params)}"
    logger.info(f"Generated auth URL: {auth_url}")
    return OAuthLoginResponse(url=auth_url)

@router.post("/refresh/token", response_model=OAuthTokenResponse)
async def refresh_token(
    request: Request,
    refresh_request: RefreshTokenRequest = Body(...)
) -> OAuthTokenResponse:
    """Refresh an access token using a refresh token"""
    # Get and validate Cognito configuration
    config = await get_validated_cognito_config()
    data = {
        "grant_type": "refresh_token",
        "client_id": config.app_client_id,
        "refresh_token": refresh_request.refresh_token
    }
    return await exchange_token(config, data, "token refresh")

@router.post("/get/token", response_model=OAuthTokenResponse)
async def get_token(
    request: Request,
    callback_request: GetTokenRequest = Body(...)
) -> OAuthTokenResponse:
    """Exchange the authorization code for an access token from any OAuth provider"""
    # Get and validate Cognito configuration
    config = await get_validated_cognito_config()
    data = {
        "grant_type": "authorization_code",
        "client_id": config.app_client_id,
        "code": callback_request.code,
        "redirect_uri": config.callback_url,
        "scope": "openid email",
    }
    return await exchange_token(config, data, "token exchange")