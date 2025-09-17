"""
FastAPI app for Farm AI Assistant | खेत सहायक AI
Serves API endpoints and static frontend files with production-ready security.
"""

import shutil
import tempfile
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from pydantic import BaseModel

from agriassist.handlers import validate_and_handle, FileHandler, InputValidator
from agriassist.config import load_env_and_models, settings
import logging

logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Global model instance
model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    global model
    try:
        # Startup
        logger.info("Starting up AgriAssist application...")
        model = load_env_and_models()
        logger.info("Application startup complete")
        yield
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down AgriAssist application...")

app = FastAPI(
    title=settings.app_name,
    description="AI-powered farming assistant providing multimodal advice",
    version="0.1.0",
    lifespan=lifespan
)

# Security middleware
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.agriassist.com"]
)

# CORS with restricted origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# Response models
class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    text: str
    audio: Optional[str] = None
    status: str = "success"

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    message: str
    version: str = "0.1.0"

# Directory for generated audio responses
AUDIO_DIR = Path(__file__).parent / "generated_speech_responses"
AUDIO_DIR.mkdir(exist_ok=True)

# Rate limit exceeded handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="AgriAssist API is running"
    )

@app.post("/api/query", response_model=QueryResponse)
@limiter.limit(f"{settings.requests_per_minute}/minute")
async def query(
    request: Request,
    text: str = Form(None),
    image: UploadFile = File(None),
    audio: UploadFile = File(None)
) -> JSONResponse:
    """
    Process multimodal farming queries with rate limiting and validation.
    """
    image_path = None
    audio_path = None
    
    try:
        # Validate file sizes
        if image and image.size and not InputValidator.validate_file_size(image.size):
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Image file too large. Maximum size: {settings.max_file_size // (1024*1024)}MB"
            )
        
        if audio and audio.size and not InputValidator.validate_file_size(audio.size):
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Audio file too large. Maximum size: {settings.max_file_size // (1024*1024)}MB"
            )
        
        # Handle file uploads securely
        if image and image.filename:
            if not FileHandler.validate_file_extension(image.filename, "image"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid image format. Allowed: JPG, PNG, GIF, BMP, WebP"
                )
            
            safe_filename = FileHandler.get_safe_filename(image.filename)
            image_path = Path(tempfile.gettempdir()) / safe_filename
            
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
        
        if audio and audio.filename:
            if not FileHandler.validate_file_extension(audio.filename, "audio"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid audio format. Allowed: MP3, WAV, M4A, OGG, FLAC, AAC"
                )
            
            safe_filename = FileHandler.get_safe_filename(audio.filename)
            audio_path = Path(tempfile.gettempdir()) / safe_filename
            
            with open(audio_path, "wb") as buffer:
                shutil.copyfileobj(audio.file, buffer)
        
        # Process the query
        text_response, audio_response = validate_and_handle(
            text, str(image_path) if image_path else None, 
            str(audio_path) if audio_path else None, 
            model=model
        )
        
        # Prepare response
        audio_url = None
        if audio_response:
            audio_filename = Path(audio_response).name
            audio_url = f"/audio/{audio_filename}"
        
        return JSONResponse({
            "text": text_response,
            "audio": audio_url,
            "status": "success"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in query endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )

# Mount static frontend and audio files
# Try Docker-specific path first, fallback to development path
DOCKER_FRONTEND_DIR = Path("/app/frontend")
DEV_FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend"
FRONTEND_DIR = DOCKER_FRONTEND_DIR if DOCKER_FRONTEND_DIR.exists() else DEV_FRONTEND_DIR

app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
