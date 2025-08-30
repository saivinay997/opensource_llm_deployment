"""
Pydantic models for the LLM Deployment Service
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional


class ModelRequest(BaseModel):
    """Request model for deploying a new model."""
    model_config = ConfigDict(protected_namespaces=())
    
    model_name: str
    device: Optional[str] = "cpu"  # CPU-only for VM compatibility
    load_in_8bit: Optional[bool] = False  # Disabled for CPU-only
    load_in_4bit: Optional[bool] = False  # Disabled for CPU-only
    trust_remote_code: Optional[bool] = True
    hf_token: Optional[str] = None


class QueryRequest(BaseModel):
    """Request model for querying the deployed model."""
    model_config = ConfigDict(protected_namespaces=())
    
    prompt: str
    max_length: Optional[int] = 512
    max_new_tokens: Optional[int] = None  # If provided, will override max_length calculation
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    top_k: Optional[int] = 50
    do_sample: Optional[bool] = True
    num_return_sequences: Optional[int] = 1


class QueryResponse(BaseModel):
    """Response model for query results."""
    model_config = ConfigDict(protected_namespaces=())
    
    response: str
    model_name: str
    generation_time: float
    input_tokens: int
    output_tokens: int


class ModelStatus(BaseModel):
    """Response model for model status."""
    model_config = ConfigDict(protected_namespaces=())
    
    model_name: Optional[str]
    is_loaded: bool
    is_loading: bool
    device: Optional[str]
