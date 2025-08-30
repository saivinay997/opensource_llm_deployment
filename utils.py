"""
Utility functions for the LLM Deployment Service
"""

import logging
import psutil
import os
import sys
from typing import Dict, Any, List


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def check_system_resources() -> Dict[str, Any]:
    """Check system resources and return status."""
    try:
        # Memory check
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024**3)
        available_gb = memory.available / (1024**3)
        used_gb = memory.used / (1024**3)
        
        # CPU check
        cpu_count = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Disk check
        disk = psutil.disk_usage('/')
        disk_total_gb = disk.total / (1024**3)
        disk_free_gb = disk.free / (1024**3)
        
        return {
            "memory": {
                "total_gb": total_gb,
                "available_gb": available_gb,
                "used_gb": used_gb,
                "percent": memory.percent
            },
            "cpu": {
                "cores": cpu_count,
                "usage_percent": cpu_percent
            },
            "disk": {
                "total_gb": disk_total_gb,
                "free_gb": disk_free_gb
            }
        }
    except Exception as e:
        logging.error(f"Error checking system resources: {e}")
        return {}


def get_model_recommendations(available_ram_gb: float) -> List[str]:
    """Get model recommendations based on available RAM."""
    if available_ram_gb < 8:
        return ["gpt2", "distilgpt2"]
    elif available_ram_gb < 16:
        return ["microsoft/DialoGPT-medium", "EleutherAI/gpt-neo-125M"]
    elif available_ram_gb < 32:
        return ["facebook/opt-350m", "microsoft/DialoGPT-large"]
    else:
        return ["openai/gpt-oss-20b", "other large models"]


def format_error_message(error: str) -> str:
    """Format error messages with helpful suggestions."""
    if "ModelWrapper" in error or "tokenizer" in error.lower():
        error += "\n\n💡 GPT-OSS-20B Compatibility Issue:\n"
        error += "This model has known compatibility issues with the current transformers version.\n"
        error += "\n💡 Try these alternative models instead:\n"
        error += "• microsoft/DialoGPT-medium (recommended for testing)\n"
        error += "• gpt2 (very reliable)\n"
        error += "• distilgpt2 (smaller, faster)\n"
        error += "• EleutherAI/gpt-neo-125M\n"
        error += "• facebook/opt-125m\n"
        error += "• microsoft/DialoGPT-large (if you have enough RAM)\n"
        error += "\n💡 For GPT-OSS-20B specifically:\n"
        error += "• Try updating transformers: pip install --upgrade transformers\n"
        error += "• Or use a different model for now\n"
    elif "out of memory" in error.lower() or "oom" in error.lower():
        error += "\n\n💡 Memory optimization suggestions:\n"
        error += "• Try a smaller model (gpt2, distilgpt2)\n"
        error += "• Ensure you have at least 32GB RAM for gpt-oss-20b\n"
        error += "• Consider using model offloading\n"
        error += "• Try microsoft/DialoGPT-medium instead\n"
    
    return error


def is_large_model(model_name: str) -> bool:
    """Check if a model is considered large."""
    large_indicators = ["20b", "gpt-oss", "70b", "175b"]
    return any(indicator in model_name.lower() for indicator in large_indicators)


def validate_model_name(model_name: str) -> bool:
    """Validate model name format."""
    if not model_name or not isinstance(model_name, str):
        return False
    
    # Basic validation - should contain organization/model format
    if "/" not in model_name:
        return False
    
    return True


def get_model_size_category(model_name: str) -> str:
    """Get the size category of a model."""
    if is_large_model(model_name):
        return "xlarge"
    elif any(size in model_name.lower() for size in ["7b", "13b"]):
        return "large"
    elif any(size in model_name.lower() for size in ["1b", "2b", "3b"]):
        return "medium"
    else:
        return "small"
