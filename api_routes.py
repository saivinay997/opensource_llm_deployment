"""
API Routes for the LLM Deployment Service
Contains all FastAPI route handlers
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

from models import ModelRequest, QueryRequest, QueryResponse, ModelStatus
from model_manager import ModelManager

# Create router
router = APIRouter()

# Global model manager instance
model_manager = ModelManager()

# Thread pool for model operations
executor = ThreadPoolExecutor(max_workers=1)


@router.post("/deploy", response_model=Dict[str, Any])
async def deploy_model(model_request: ModelRequest, background_tasks: BackgroundTasks):
    """Deploy a new model from Hugging Face."""
    
    if model_manager.is_loading:
        raise HTTPException(status_code=400, detail="Model is currently loading. Please wait.")
    
    if model_manager.model is not None or model_manager.generator is not None:
        raise HTTPException(status_code=400, detail="Model is already loaded. Use /undeploy to unload first.")
    
    device = model_manager.get_device(model_request.device)
    model_manager.set_model_name(model_request.model_name)
    
    # Start loading in background (CPU-only, quantization disabled)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        executor,
        model_manager.load_model_sync,
        model_request.model_name,
        device,
        False,  # load_in_8bit disabled for CPU
        False,  # load_in_4bit disabled for CPU
        model_request.trust_remote_code,
        model_request.hf_token
    )
    
    return {
        "message": f"Model {model_request.model_name} is being loaded on {device}",
        "model_name": model_request.model_name,
        "device": device,
        "status": "loading"
    }


@router.post("/query", response_model=QueryResponse)
async def query_model(query_request: QueryRequest):
    """Query the deployed model."""
    try:
        result = model_manager.generate_response(
            prompt=query_request.prompt,
            max_length=query_request.max_length,
            temperature=query_request.temperature,
            top_p=query_request.top_p,
            top_k=query_request.top_k,
            do_sample=query_request.do_sample,
            num_return_sequences=query_request.num_return_sequences
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=ModelStatus)
async def get_model_status():
    """Get the current status of the model."""
    status = model_manager.get_status()
    return ModelStatus(**status)


@router.delete("/undeploy")
async def undeploy_model():
    """Undeploy the current model and free memory."""
    try:
        model_manager.unload_model()
        return {"message": "Model undeployed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@router.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Open Source LLM Deployment Service",
        "version": "1.0.0",
        "endpoints": {
            "deploy": "POST /deploy - Deploy a model from Hugging Face",
            "query": "POST /query - Query the deployed model",
            "status": "GET /status - Get model status",
            "undeploy": "DELETE /undeploy - Undeploy current model"
        },
        "web_interface": "GET /web-interface - Access the web interface",
        "supported_models": "Any Hugging Face model supported"
    }
