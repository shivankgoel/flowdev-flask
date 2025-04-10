from fastapi import Request, HTTPException, Depends
import os
import jwt
from jose import jwt as jose_jwt
import requests
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class CognitoAuth:
    """Handles customer authentication."""
    
    # Cognito configuration
    COGNITO_REGION = os.getenv('COGNITO_REGION', 'us-east-1')
    COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
    COGNITO_APP_CLIENT_ID = os.getenv('COGNITO_APP_CLIENT_ID')
    
    @staticmethod
    def get_cognito_public_keys() -> dict:
        """Get public keys from Cognito."""
        url = f'https://cognito-idp.{CognitoAuth.COGNITO_REGION}.amazonaws.com/{CognitoAuth.COGNITO_USER_POOL_ID}/.well-known/jwks.json'
        response = requests.get(url)
        return response.json()
    
    @staticmethod
    def verify_cognito_token(token: str) -> Optional[str]:
        """Verify Cognito token and return customer ID."""
        try:
            # Get token header to find the right key
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get('kid')
            
            # Get public keys
            public_keys = CognitoAuth.get_cognito_public_keys()
            key = next((key for key in public_keys['keys'] if key['kid'] == kid), None)
            if not key:
                return None
            
            # Verify token
            claims = jose_jwt.decode(
                token,
                key,
                algorithms=['RS256'],
                audience=CognitoAuth.COGNITO_APP_CLIENT_ID
            )
            
            # Return customer ID (sub claim)
            return claims.get('sub')
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return None
    
    @staticmethod
    async def get_customer_id(request: Request) -> str:
        """Get customer ID from request.
        
        In development mode, returns a mock customer ID.
        In production mode, verifies Cognito token and returns customer ID.
        """
        # Get environment and log it
        env = os.getenv('FLASK_ENV', 'production').lower()
        logger.info(f"Environment check - FLASK_ENV: {env}")
        logger.info(f"Environment check - All env vars: {dict(os.environ)}")
        
        if env == 'development':
            mock_id = os.getenv('MOCK_CUSTOMER_ID', 'test-customer-123')
            logger.info(f"Development mode - Using mock customer ID: {mock_id}")
            return mock_id
            
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning("Missing or invalid Authorization header")
            raise HTTPException(status_code=401, detail="Missing Authorization header")
            
        token = auth_header.split(' ')[1]
        customer_id = CognitoAuth.verify_cognito_token(token)
        
        if not customer_id:
            logger.warning("Invalid or expired token")
            raise HTTPException(status_code=401, detail="Invalid or expired token")
            
        logger.info(f"Successfully verified token for customer: {customer_id}")
        return customer_id 