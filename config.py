"""
Configuration settings for the LLM Deployment Service
"""

import os
from typing import Optional


class Settings:
    """Application settings."""
    
    # API Settings
    API_TITLE: str = "Open Source LLM Deployment Service"
    API_DESCRIPTION: str = "A FastAPI service for deploying and querying open-source LLMs from Hugging Face"
    API_VERSION: str = "1.0.0"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Model Settings
    DEFAULT_DEVICE: str = "cpu"
    DEFAULT_MAX_LENGTH: int = 512
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_TOP_P: float = 0.9
    DEFAULT_TOP_K: int = 50
    
    # Thread Pool Settings
    MAX_WORKERS: int = 1
    
    # Memory Settings
    LOW_CPU_MEM_USAGE: bool = True
    OFFLOAD_FOLDER: str = "offload"
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    
    # CORS Settings
    ALLOW_ORIGINS: list = ["*"]
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: list = ["*"]
    ALLOW_HEADERS: list = ["*"]
    
    # Model Recommendations
    RECOMMENDED_MODELS = {
        "small": ["gpt2", "distilgpt2"],
        "medium": ["microsoft/DialoGPT-medium", "EleutherAI/gpt-neo-125M"],
        "large": ["facebook/opt-350m", "microsoft/DialoGPT-large"],
        "xlarge": ["facebook/opt-1.3b", "microsoft/DialoGPT-large"]
    }
    
    # Memory Requirements (in GB)
    MEMORY_REQUIREMENTS = {
        "small": 4,
        "medium": 8,
        "large": 16,
        "xlarge": 32
    }


# Create global settings instance
settings = Settings()
