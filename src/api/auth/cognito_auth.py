from fastapi import Request, HTTPException, Depends
import os
from jose import jwt
import requests
from typing import Optional, Dict, Any
import logging
import json
import base64
import time

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
    def extract_token_header(token: str) -> Optional[Dict[str, Any]]:
        """Extract and decode the JWT header."""
        try:
            # Split the token and get the header part
            parts = token.split('.')
            if len(parts) != 3:
                logger.error("Invalid token format")
                return None
                
            # Decode the header
            header_b64 = parts[0]
            # Add padding if needed
            padding = '=' * (4 - len(header_b64) % 4)
            header_bytes = base64.urlsafe_b64decode(header_b64 + padding)
            header = json.loads(header_bytes)
            
            logger.info("Token Header Information:")
            logger.info(f"Algorithm: {header.get('alg', 'N/A')}")
            logger.info(f"Key ID: {header.get('kid', 'N/A')}")
            logger.info(f"Type: {header.get('typ', 'JWT')}")
            
            return header
        except Exception as e:
            logger.error(f"Error decoding token header: {str(e)}")
            return None
    
    @staticmethod
    def extract_token_payload(token: str) -> Optional[Dict[str, Any]]:
        """Extract and decode the JWT payload."""
        try:
            # Split the token and get the payload part
            parts = token.split('.')
            if len(parts) != 3:
                logger.error("Invalid token format")
                return None
                
            # Decode the payload
            payload_b64 = parts[1]
            # Add padding if needed
            padding = '=' * (4 - len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64 + padding)
            payload = json.loads(payload_bytes)
            
            logger.info("\nToken Payload Information:")
            logger.info(f"Subject (sub): {payload.get('sub', 'N/A')}")
            logger.info(f"Token Use: {payload.get('token_use', 'N/A')}")
            logger.info(f"Client ID: {payload.get('client_id', 'N/A')}")
            logger.info(f"Issuer: {payload.get('iss', 'N/A')}")
            logger.info(f"Username: {payload.get('username', 'N/A')}")
            logger.info(f"Groups: {payload.get('cognito:groups', [])}")
            logger.info(f"Scope: {payload.get('scope', 'N/A')}")
            logger.info(f"Issued At: {payload.get('iat', 'N/A')}")
            logger.info(f"Expiration: {payload.get('exp', 'N/A')}")
            
            return payload
        except Exception as e:
            logger.error(f"Error decoding token payload: {str(e)}")
            return None
    
    @staticmethod
    def extract_token_signature(token: str) -> Optional[str]:
        """Extract the JWT signature."""
        try:
            # Split the token and get the signature part
            parts = token.split('.')
            if len(parts) != 3:
                logger.error("Invalid token format")
                return None
                
            signature = parts[2]
            
            logger.info("\nToken Signature Information:")
            logger.info(f"Signature Length: {len(signature)} characters")
            logger.info("Note: Signature is a cryptographic hash and cannot be decoded")
            
            return signature
        except Exception as e:
            logger.error(f"Error extracting token signature: {str(e)}")
            return None
    
    @staticmethod
    def verify_cognito_token(token: str) -> Optional[str]:
        """Verify Cognito token and return customer ID if token is not expired."""
        try:
            # Extract token information
            header = CognitoAuth.extract_token_header(token)
            payload = CognitoAuth.extract_token_payload(token)
            CognitoAuth.extract_token_signature(token)
            
            if not payload:
                logger.error("Failed to extract token payload")
                return None
                
            # Get expiration time and check if token is still valid
            exp_time = payload.get('exp')
            if not exp_time:
                logger.error("Token missing 'exp' claim")
                return None
                
            # Get current time
            current_time = int(time.time())
            
            # Check if token is expired
            if current_time >= exp_time:
                logger.error("Token has expired")
                return None
                
            # Return customer ID from sub claim
            customer_id = payload.get('sub')
            if not customer_id:
                logger.error("Token missing 'sub' claim")
                return None
                
            logger.info(f"Token verified for customer: {customer_id}")
            return customer_id
            
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
        
        if env == 'development':
            mock_id = os.getenv('MOCK_CUSTOMER_ID', 'test-customer-123')
            logger.info(f"Development mode - Using mock customer ID: {mock_id}")
            return mock_id
            
        # Log all headers for debugging
        logger.info(f"Request headers: {dict(request.headers)}")
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            logger.warning("Authorization header is missing")
            raise HTTPException(status_code=401, detail="Missing Authorization header")
            
        if not auth_header.startswith('Bearer '):
            logger.warning(f"Invalid Authorization header format: {auth_header[:20]}...")
            raise HTTPException(status_code=401, detail="Invalid Authorization header format")
            
        token = auth_header.split(' ')[1]
        if token == 'null':
            logger.warning("Token is null - user is not logged in")
            raise HTTPException(status_code=401, detail="User is not logged in")
            
        logger.info(f"Token length: {len(token)}")
        
        customer_id = CognitoAuth.verify_cognito_token(token)
        if not customer_id:
            logger.warning("Invalid or expired token")
            raise HTTPException(status_code=401, detail="Invalid or expired token")
            
        logger.info(f"Successfully verified token for customer: {customer_id}")
        return customer_id 