from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class AuthCheckRequest(BaseModel):
    """Request model for auth check endpoint"""
    pass

class GetCurrentUserRequest(BaseModel):
    """Request model for get current user endpoint"""
    pass

class LogoutRequest(BaseModel):
    """Request model for logout endpoint"""
    refresh_token: str = Field(..., description="Refresh token to revoke")

class AuthCheckResponse(BaseModel):
    """Response model for auth check endpoint"""
    authenticated: bool = Field(..., description="Whether the user is authenticated")
    customer_id: Optional[str] = Field(None, description="Customer ID if authenticated")

class UserData(BaseModel):
    """User data model"""
    customer_id: str = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")

class GetCurrentUserResponse(BaseModel):
    """Response model for get current user endpoint"""
    user: UserData = Field(..., description="Current user's data")

class LogoutResponse(BaseModel):
    """Response model for logout endpoint"""
    message: str = Field(..., description="Logout status message")
    logout_url: Optional[str] = Field(None, description="URL to redirect to for completing logout")

class OAuthLoginRequest(BaseModel):
    """Base request model for OAuth login"""
    redirect_uri: Optional[str] = Field(None, description="Custom redirect URI for OAuth flow")

class OAuthLoginResponse(BaseModel):
    """Response model for OAuth login endpoints"""
    url: str = Field(None, description="URL to redirect to for OAuth authentication")

class GoogleLoginRequest(OAuthLoginRequest):
    """Request model for Google login"""
    pass

class GitHubLoginRequest(OAuthLoginRequest):
    """Request model for GitHub login"""
    pass


class RefreshTokenRequest(BaseModel):
    """Request model for refresh token"""
    refresh_token: str = Field(..., description="Refresh token to refresh")

class GetTokenRequest(BaseModel):
    """Request model for OAuth callback"""
    code: str = Field(..., description="Authorization code from OAuth provider")
    state: Optional[str] = Field(None, description="State parameter for CSRF protection")

class OAuthTokenResponse(BaseModel):
    """Response model for OAuth token exchange"""
    access_token: str = Field(..., description="Access token for API calls")
    refresh_token: Optional[str] = Field(None, description="Refresh token for getting new access tokens")
    id_token: Optional[str] = Field(None, description="ID token containing user information")
    token_type: str = Field(..., description="Type of token (usually 'Bearer')")
    expires_in: int = Field(..., description="Token expiration time in seconds")

class CognitoConfig(BaseModel):
    """Cognito configuration settings"""
    region: str = Field(default="us-east-1", description="AWS region for Cognito")
    user_pool_id: str = Field(..., description="Cognito User Pool ID")
    app_client_id: str = Field(..., description="Cognito App Client ID")
    app_client_secret: str = Field(..., description="Cognito App Client Secret")
    domain: str = Field(..., description="Cognito Domain")
    callback_url: str = Field(..., description="OAuth callback URL") 