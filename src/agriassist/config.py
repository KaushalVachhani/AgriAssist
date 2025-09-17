import os
import logging
from typing import Any, List
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings
import google.generativeai as genai

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application configuration settings."""
    
    # API Keys
    groq_api_key: str = Field(..., env="GROQ_API_KEY")
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    
    # Application settings
    app_name: str = Field("Farm AI Assistant", env="APP_NAME")
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # Security settings
    allowed_origins: List[str] = Field(
        ["http://localhost:3000", "http://localhost:7860", "http://127.0.0.1:7860"],
        env="ALLOWED_ORIGINS"
    )
    max_file_size: int = Field(10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    
    # Model settings
    gemini_model_name: str = Field("gemini-2.5-flash", env="GEMINI_MODEL_NAME")
    whisper_model_name: str = Field("whisper-large-v3", env="WHISPER_MODEL_NAME")
    
    # Rate limiting
    requests_per_minute: int = Field(30, env="REQUESTS_PER_MINUTE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

def get_settings() -> Settings:
    """Get application settings."""
    load_dotenv()
    return Settings()

def configure_logging(log_level: str = "INFO") -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
        ]
    )

def load_env_and_models() -> Any:
    """
    Load environment variables and initialize the Gemini model.
    Raises ValueError if any required environment variable is missing.
    Returns the initialized generative model.
    """
    settings = get_settings()
    configure_logging(settings.log_level)
    
    try:
        genai.configure(api_key=settings.google_api_key)
        model = genai.GenerativeModel(model_name=settings.gemini_model_name)
        logger.info(f"Successfully initialized {settings.gemini_model_name} model")
        return model
    except Exception as e:
        logger.error(f"Failed to initialize model: {e}")
        raise ValueError(f"Failed to initialize AI model: {e}")

# Global settings instance
settings = get_settings()
