from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.canvas_api import router
import os
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

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

# Include the router
app.include_router(router)

@app.get("/")
async def root():
    """Redirect root to API documentation"""
    return {"message": "Welcome to the Canvas API. Visit /docs for documentation."}

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    uvicorn.run(app, host="0.0.0.0", port=port) 