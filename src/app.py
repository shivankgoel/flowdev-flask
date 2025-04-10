from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.canvas_api import router as canvas_router
from src.api.auth.routes import router as auth_router
import os
from dotenv import load_dotenv
import uvicorn
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler()  # This will print to console
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
logger.info(f"Loading environment from: {env_path}")

if not os.path.exists(env_path):
    logger.warning(f".env file not found at {env_path}")
else:
    logger.info("Found .env file, loading environment variables")
    load_dotenv(env_path)

# Log all relevant environment variables
env = os.getenv('FLASK_ENV', 'production').lower()
logger.info(f"FLASK_ENV: {env}")
logger.info(f"COGNITO_REGION: {os.getenv('COGNITO_REGION')}")
logger.info(f"COGNITO_USER_POOL_ID: {os.getenv('COGNITO_USER_POOL_ID')}")
logger.info(f"COGNITO_APP_CLIENT_ID: {os.getenv('COGNITO_APP_CLIENT_ID')}")
logger.info(f"COGNITO_DOMAIN: {os.getenv('COGNITO_DOMAIN')}")

# Create FastAPI app with OpenAPI configuration
app = FastAPI(
    title="Canvas API",
    description="API for managing canvases",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include the routers
app.include_router(canvas_router)
app.include_router(auth_router)

@app.get("/")
async def root():
    """Redirect root to API documentation"""
    return {"message": "Welcome to the Canvas API. Visit /docs for documentation."}

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    uvicorn.run(app, host="0.0.0.0", port=port) 