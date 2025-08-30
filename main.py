from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Open Source LLM Deployment Service",
    description="A FastAPI service for deploying and querying open-source LLMs from Hugging Face",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="."), name="static")

# Global variables to store the model and tokenizer
model = None
tokenizer = None
generator = None
model_name = None
is_loading = False

# Thread pool for model operations
executor = ThreadPoolExecutor(max_workers=1)

class ModelRequest(BaseModel):
    model_name: str
    device: Optional[str] = "cpu"  # CPU-only for VM compatibility
    load_in_8bit: Optional[bool] = False  # Disabled for CPU-only
    load_in_4bit: Optional[bool] = False  # Disabled for CPU-only
    trust_remote_code: Optional[bool] = True
    hf_token: Optional[str] = None

class QueryRequest(BaseModel):
    prompt: str
    max_length: Optional[int] = 512
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    top_k: Optional[int] = 50
    do_sample: Optional[bool] = True
    num_return_sequences: Optional[int] = 1

class QueryResponse(BaseModel):
    response: str
    model_name: str
    generation_time: float
    input_tokens: int
    output_tokens: int

class ModelStatus(BaseModel):
    model_name: Optional[str]
    is_loaded: bool
    is_loading: bool
    device: Optional[str]

def get_device(device_preference: str) -> str:
    """Determine the best available device (CPU-only)."""
    # Force CPU usage for VM compatibility
    return "cpu"

def load_model_sync(model_name: str, device: str, load_in_8bit: bool, load_in_4bit: bool, trust_remote_code: bool, hf_token: str = None):
    """Load model synchronously in a separate thread."""
    global model, tokenizer, generator, is_loading
    
    try:
        logger.info(f"Loading model: {model_name}")
        is_loading = True
        
        # Check for quantization dependencies
        if load_in_8bit or load_in_4bit:
            try:
                import accelerate
                import bitsandbytes
                logger.info("Quantization dependencies found")
            except ImportError as e:
                logger.warning(f"Quantization dependencies not found: {e}")
                logger.warning("Falling back to full precision loading")
                load_in_8bit = False
                load_in_4bit = False
        
        # Load tokenizer
        tokenizer_kwargs = {"trust_remote_code": trust_remote_code}
        if hf_token:
            tokenizer_kwargs["token"] = hf_token
            
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            **tokenizer_kwargs
        )
        
        # Add padding token if not present
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Load model (CPU-only, no quantization for VM compatibility)
        model_kwargs = {
            "trust_remote_code": trust_remote_code,
            "device_map": None,  # Force CPU loading
        }
        
        if hf_token:
            model_kwargs["token"] = hf_token
        
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            **model_kwargs
        )
        
        # Ensure model is on CPU
        model = model.to("cpu")
        
        # Create text generation pipeline (CPU-only)
        generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device="cpu",
        )
        
        logger.info(f"Model {model_name} loaded successfully on {device}")
        is_loading = False
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        is_loading = False
        raise e

@app.post("/deploy", response_model=Dict[str, Any])
async def deploy_model(model_request: ModelRequest, background_tasks: BackgroundTasks):
    """Deploy a new model from Hugging Face."""
    global model_name
    
    if is_loading:
        raise HTTPException(status_code=400, detail="Model is currently loading. Please wait.")
    
    if model is not None:
        raise HTTPException(status_code=400, detail="Model is already loaded. Use /undeploy to unload first.")
    
    device = get_device(model_request.device)
    model_name = model_request.model_name
    
    # Start loading in background (CPU-only, quantization disabled)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        executor,
        load_model_sync,
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

@app.post("/query", response_model=QueryResponse)
async def query_model(query_request: QueryRequest):
    """Query the deployed model."""
    global model, tokenizer, generator, model_name
    
    if model is None or tokenizer is None:
        raise HTTPException(status_code=400, detail="No model is currently loaded. Please deploy a model first.")
    
    if is_loading:
        raise HTTPException(status_code=400, detail="Model is currently loading. Please wait.")
    
    try:
        start_time = time.time()
        
        # Tokenize input
        inputs = tokenizer(query_request.prompt, return_tensors="pt")
        input_tokens = inputs.input_ids.shape[1]
        
        # Generate response
        generation_kwargs = {
            "max_length": query_request.max_length,
            "temperature": query_request.temperature,
            "top_p": query_request.top_p,
            "top_k": query_request.top_k,
            "do_sample": query_request.do_sample,
            "num_return_sequences": query_request.num_return_sequences,
            "pad_token_id": tokenizer.eos_token_id,
        }
        
        # Generate using pipeline
        outputs = generator(query_request.prompt, **generation_kwargs)
        
        # Extract generated text
        generated_text = outputs[0]['generated_text']
        response_text = generated_text[len(query_request.prompt):].strip()
        
        # Count output tokens
        output_tokens = len(tokenizer.encode(response_text))
        
        generation_time = time.time() - start_time
        
        return QueryResponse(
            response=response_text,
            model_name=model_name,
            generation_time=generation_time,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )
        
    except Exception as e:
        logger.error(f"Error during generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")

@app.get("/status", response_model=ModelStatus)
async def get_model_status():
    """Get the current status of the model."""
    global model, model_name, is_loading
    
    device = "unknown"
    if model is not None:
        if hasattr(model, 'device'):
            device = str(model.device)
        elif hasattr(model, 'hf_device_map'):
            device = str(model.hf_device_map)
    
    return ModelStatus(
        model_name=model_name,
        is_loaded=model is not None,
        is_loading=is_loading,
        device=device
    )

@app.delete("/undeploy")
async def undeploy_model():
    """Undeploy the current model and free memory."""
    global model, tokenizer, generator, model_name
    
    if model is None:
        raise HTTPException(status_code=400, detail="No model is currently loaded.")
    
    try:
        # Clear model references
        del model
        del tokenizer
        del generator
        
        # Force garbage collection
        import gc
        gc.collect()
        
        # CPU-only: no CUDA cache to clear
        pass
        
        model = None
        tokenizer = None
        generator = None
        model_name = None
        
        return {"message": "Model undeployed successfully"}
        
    except Exception as e:
        logger.error(f"Error undeploying model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Undeploy error: {str(e)}")

@app.get("/")
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
        "web_interface": "GET /web-interface - Access the web interface"
    }

@app.get("/web-interface")
async def web_interface():
    """Serve the web interface."""
    return FileResponse("web_interface.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
