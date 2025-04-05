from functools import wraps
from fastapi import Request, HTTPException, Depends
import jwt
from typing import Optional, Dict
import os
import requests
from jose.exceptions import JWTError

class CognitoAuth:
    """Handles AWS Cognito authentication for API endpoints."""
    
    # Development mode flag
    DEV_MODE = os.getenv('FLASK_ENV', 'production').lower() == 'development'
    
    # Cognito configuration
    COGNITO_REGION = os.getenv('COGNITO_REGION', 'your-cognito-region')
    COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID', 'your-user-pool-id')
    COGNITO_APP_CLIENT_ID = os.getenv('COGNITO_APP_CLIENT_ID', 'your-app-client-id')

    @staticmethod
    def get_cognito_public_keys():
        """Fetch the public keys from Cognito."""
        url = f'https://cognito-idp.{CognitoAuth.COGNITO_REGION}.amazonaws.com/{CognitoAuth.COGNITO_USER_POOL_ID}/.well-known/jwks.json'
        response = requests.get(url)
        return response.json()

    @staticmethod
    def verify_cognito_token(token: str) -> Dict:
        """Verify the token using Cognito's public keys."""
        if CognitoAuth.DEV_MODE:
            # In development mode, return a mock user
            return {
                'sub': os.getenv('MOCK_CUSTOMER_ID', 'test-customer-123'),
                'email': os.getenv('MOCK_USER_EMAIL', 'test@example.com'),
                'cognito:username': os.getenv('MOCK_USERNAME', 'test-user')
            }
            
        try:
            public_keys = CognitoAuth.get_cognito_public_keys()
            header = jwt.get_unverified_header(token)
            key = next((key for key in public_keys['keys'] if key['kid'] == header['kid']), None)
            if not key:
                raise JWTError('Invalid token')
            return jwt.decode(token, key, algorithms=['RS256'], audience=CognitoAuth.COGNITO_APP_CLIENT_ID)
        except JWTError:
            raise JWTError('Invalid token')

    @staticmethod
    def get_cognito_identity(request: Request) -> Optional[str]:
        """Extract customer_id from Cognito identity token or use mock for development.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Optional[str]: The customer ID (Cognito user ID) if token is valid, None otherwise
        """
        if CognitoAuth.DEV_MODE:
            # In development mode, use a mock customer ID
            return os.getenv('MOCK_CUSTOMER_ID', 'test-customer-123')
            
        # Production mode - use actual Cognito token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        try:
            # Verify the token with Cognito
            decoded = CognitoAuth.verify_cognito_token(token)
            return decoded.get('sub')  # sub is the Cognito user ID
        except Exception as e:
            print(f"Error decoding token: {str(e)}")
            return None

    @staticmethod
    async def require_auth(request: Request) -> str:
        """FastAPI dependency for requiring Cognito authentication."""
        customer_id = CognitoAuth.get_cognito_identity(request)
        if not customer_id:
            raise HTTPException(status_code=401, detail="Unauthorized - Invalid or missing Cognito token")
        return customer_id 