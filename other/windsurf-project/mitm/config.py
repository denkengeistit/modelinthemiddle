import os
from typing import Dict, Any
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # LLM configuration
    LOCAL_LLM_ENDPOINT: str = "http://localhost:5000/generate"
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.7
    
    # Tool discovery
    TOOL_DISCOVERY_INTERVAL: int = 300  # seconds
    MAX_TOOLS_PER_PAGE: int = 10
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Initialize settings
settings = Settings()
