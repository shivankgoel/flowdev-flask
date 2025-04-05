from typing import Optional
from pydantic import BaseSettings

class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    DYNAMODB_REGION: str = "us-east-1"
    DYNAMODB_ENDPOINT_URL: Optional[str] = None
    DYNAMODB_ACCESS_KEY_ID: Optional[str] = None
    DYNAMODB_SECRET_ACCESS_KEY: Optional[str] = None
    
    class Config:
        env_prefix = "FLOW_"
        case_sensitive = True

db_settings = DatabaseSettings() 