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
    AuthCheckRequest,
    AuthCheckResponse,
    GetCurrentUserRequest,
    GetCurrentUserResponse,
    LogoutRequest,
    LogoutResponse,
    OAuthLoginResponse,
    GoogleLoginRequest,
    GitHubLoginRequest,
    OAuthCallbackRequest,
    OAuthTokenResponse,
    UserData
)

router = APIRouter(prefix="/auth", tags=["auth"])

def get_cognito_config() -> Dict[str, str]:
    """Get Cognito configuration from environment variables"""
    config = {
        'region': os.getenv('COGNITO_REGION', 'us-east-1'),
        'user_pool_id': os.getenv('COGNITO_USER_POOL_ID'),
        'app_client_id': os.getenv('COGNITO_APP_CLIENT_ID'),
        'app_client_secret': os.getenv('COGNITO_APP_CLIENT_SECRET'),
        'domain': os.getenv('COGNITO_DOMAIN'),
        'callback_url': os.getenv('COGNITO_CALLBACK_URL')
    }
    return config

def validate_cognito_config(config: Dict[str, str]) -> Optional[str]:
    """Validate Cognito configuration and return error message if invalid"""
    missing_configs = []
    if not config['user_pool_id']:
        missing_configs.append("COGNITO_USER_POOL_ID")
    if not config['app_client_id']:
        missing_configs.append("COGNITO_APP_CLIENT_ID")
    if not config['app_client_secret']:
        missing_configs.append("COGNITO_APP_CLIENT_SECRET")
    if not config['domain']:
        missing_configs.append("COGNITO_DOMAIN")
    if not config['callback_url']:
        missing_configs.append("COGNITO_CALLBACK_URL")
    
    if missing_configs:
        return f"Missing Cognito configuration: {', '.join(missing_configs)}"
    return None

@router.get("/check", response_model=AuthCheckResponse)
async def check_auth(
    request: Request,
    _: AuthCheckRequest = Depends()
) -> AuthCheckResponse:
    """Check if user is authenticated"""
    try:
        customer_id = await CognitoAuth.get_customer_id(request)
        return AuthCheckResponse(authenticated=True, customer_id=customer_id)
    except HTTPException:
        return AuthCheckResponse(authenticated=False)

@router.get("/me", response_model=GetCurrentUserResponse)
async def get_current_user(
    request: Request,
    _: GetCurrentUserRequest = Depends()
) -> GetCurrentUserResponse:
    """Get current user data"""
    try:
        customer_id = await CognitoAuth.get_customer_id(request)
        # Here you would typically fetch more user details from your database
        user_data = UserData(
            id=customer_id,
            email="user@example.com",  # Replace with actual user data
        )
        return GetCurrentUserResponse(user=user_data)
    except HTTPException as e:
        raise HTTPException(status_code=401, detail="Unauthorized")

@router.api_route("/logout", methods=["GET", "POST"], response_model=LogoutResponse)
async def logout(
    request: Request,
    logout_request: LogoutRequest = Body(...)
) -> LogoutResponse:
    """Logout user from Cognito and clear local session"""
    # Get Cognito configuration
    config = get_cognito_config()
    config_error = validate_cognito_config(config)
    if config_error:
        logger.error(f"Cognito configuration error: {config_error}")
        raise HTTPException(
            status_code=500,
            detail=config_error
        )
    
    try:
        # First, revoke the refresh token
        revoke_url = f"https://{config['domain']}/oauth2/revoke"
        
        # Create Basic Auth header
        client_credentials = f"{config['app_client_id']}:{config['app_client_secret']}"
        auth_header = base64.b64encode(client_credentials.encode()).decode()
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth_header}"
        }
        
        # Send the refresh token to revoke
        revoke_data = {
            "token": logout_request.refresh_token
        }
        
        logger.info("Attempting to revoke refresh token")
        logger.info(f"Revoke URL: {revoke_url}")
        
        revoke_response = requests.post(revoke_url, headers=headers, data=revoke_data)
        revoke_response.raise_for_status()
        logger.info("Refresh token successfully revoked")
        
        return LogoutResponse(
            message="Refresh token successfully revoked",
        )
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"Error revoking token: {str(e)}")
        if e.response:
            logger.error(f"Response status: {e.response.status_code}")
            # Don't log the full response body as it might contain sensitive information
        raise HTTPException(
            status_code=500,
            detail="Failed to revoke token"
        )
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred during logout"
        )

@router.api_route("/google", methods=["GET", "POST"], response_model=OAuthLoginResponse)
async def google_login(request: Request, _: GoogleLoginRequest = Depends()) -> OAuthLoginResponse:
    """Initiate Google login through Cognito"""
    # Get and validate Cognito configuration
    config = get_cognito_config()
    config_error = validate_cognito_config(config)
    if config_error:
        logger.error(f"Cognito configuration error: {config_error}")
        raise HTTPException(
            status_code=500,
            detail=config_error
        )
    
    # Use the exact callback URL from config
    callback_url = config['callback_url']
    logger.info(f"Using Cognito domain: {config['domain']}")
    logger.info(f"Using callback URL: {callback_url}")
    logger.info(f"Full Cognito config: {config}")
    
    # Construct the Cognito hosted UI URL for Google
    params = {
        "identity_provider": "Google",
        "client_id": config['app_client_id'],
        "response_type": "code",
        "scope": "openid email",
        "redirect_uri": callback_url
    }
    
    auth_url = f"https://{config['domain']}/oauth2/authorize?{urlencode(params)}"
    logger.info(f"Generated auth URL: {auth_url}")
    return OAuthLoginResponse(url=auth_url)

@router.post("/code/callback", response_model=OAuthTokenResponse)
async def oauth_callback(
    request: Request,
    callback_request: OAuthCallbackRequest = Body(...)
) -> OAuthTokenResponse:
    """Exchange the authorization code for an access token from any OAuth provider"""
    # Get Cognito configuration
    config = get_cognito_config()
    config_error = validate_cognito_config(config)
    if config_error:
        logger.error(f"Cognito configuration error: {config_error}")
        raise HTTPException(
            status_code=500,
            detail=config_error
        )
    
    # Use the exact callback URL from config
    callback_url = config['callback_url']
    logger.info(f"Using callback URL for token exchange: {callback_url}")
    
    # Construct the token endpoint URL
    token_url = f"https://{config['domain']}/oauth2/token"
    
    # Create the Authorization header with client credentials
    client_credentials = f"{config['app_client_id']}:{config['app_client_secret']}"
    auth_header = base64.b64encode(client_credentials.encode()).decode()
    
    # Set up headers and data for the token request
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth_header}"
    }
    
    data = {
        "grant_type": "authorization_code",
        "client_id": config['app_client_id'],
        "code": callback_request.code,
        "redirect_uri": callback_url,
        "scope": "openid email",
    }
    
    try:
        # Make the request to exchange the code for a token
        response = requests.post(token_url, headers=headers, data=data)
        
        # Log only non-sensitive response information
        logger.info(f"Token exchange response status: {response.status_code}")
        logger.info("Token exchange successful")
        
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
        
    except requests.exceptions.HTTPError as e:
        error_response = e.response.json() if e.response else {}
        error_type = error_response.get('error', 'unknown_error')
        error_description = error_response.get('error_description', str(e))
        
        logger.error(f"Token exchange failed: {error_type}")
        if e.response:
            logger.error(f"Response status: {e.response.status_code}")
        raise HTTPException(
            status_code=500,
            detail=f"Token exchange failed: {error_description}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during token exchange: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during token exchange"
        )