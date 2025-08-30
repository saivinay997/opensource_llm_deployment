"""
Model Manager for LLM Deployment Service
Handles model loading, unloading, and management operations
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import logging
import time
from typing import Optional, Dict, Any

from utils import is_large_model, format_error_message
from config import settings

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages the lifecycle of LLM models."""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.generator = None
        self.model_name = None
        self.is_loading = False
    
    def get_device(self, device_preference: str) -> str:
        """Determine the best available device (CPU-only)."""
        # Force CPU usage for VM compatibility
        return "cpu"
    
    def load_model_sync(self, model_name: str, device: str, load_in_8bit: bool, 
                        load_in_4bit: bool, trust_remote_code: bool, hf_token: str = None):
        """Load model synchronously in a separate thread."""
        try:
            logger.info(f"Loading model: {model_name}")
            self.is_loading = True
            
            # Special handling for large models
            is_large_model_flag = is_large_model(model_name)
            
            if is_large_model_flag:
                logger.info("Detected large model - applying memory optimizations")
                # Force CPU-only for large models
                device = "cpu"
                load_in_8bit = False
                load_in_4bit = False
            
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
            

            
            # Standard approach for other models
            # Load tokenizer with fallback options
            tokenizer_kwargs = {"trust_remote_code": trust_remote_code}
            if hf_token:
                tokenizer_kwargs["token"] = hf_token
            
            try:
                # Try loading with fast tokenizer first
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    **tokenizer_kwargs
                )
            except Exception as e:
                logger.warning(f"Fast tokenizer failed: {e}")
                logger.info("Trying with use_fast=False...")
                
                # Fallback to slow tokenizer
                tokenizer_kwargs["use_fast"] = False
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    **tokenizer_kwargs
                )
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with optimizations for large models
            model_kwargs = {
                "trust_remote_code": trust_remote_code,
                "device_map": None,  # Force CPU loading
            }
            
            # Memory optimizations for large models
            if is_large_model_flag:
                logger.info("Applying memory optimizations for large model")
                model_kwargs.update({
                    "low_cpu_mem_usage": True,
                    "torch_dtype": torch.float32,  # Use float32 for better compatibility
                    "offload_folder": "offload",  # Enable model offloading
                })
            else:
                model_kwargs["low_cpu_mem_usage"] = True
            
            if hf_token:
                model_kwargs["token"] = hf_token
            
            try:
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    **model_kwargs
                )
            except Exception as e:
                logger.warning(f"Model loading failed with optimizations: {e}")
                logger.info("Trying with minimal settings...")
                
                # Fallback to minimal settings
                fallback_kwargs = {
                    "trust_remote_code": trust_remote_code,
                    "device_map": None,
                }
                if hf_token:
                    fallback_kwargs["token"] = hf_token
                
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    **fallback_kwargs
                )
            
            # Ensure model is on CPU
            self.model = self.model.to("cpu")
            
            # Create text generation pipeline with optimizations for large models
            pipeline_kwargs = {
                "model": self.model,
                "tokenizer": self.tokenizer,
                "device": "cpu",
            }
            
            # Add optimizations for large models
            if is_large_model_flag:
                logger.info("Applying pipeline optimizations for large model")
                pipeline_kwargs.update({
                    "model_kwargs": {"low_cpu_mem_usage": True},
                })
            
            self.generator = pipeline("text-generation", **pipeline_kwargs)
            
            logger.info(f"Model {model_name} loaded successfully on {device}")
            self.is_loading = False
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self.is_loading = False
            
            # Provide helpful error message with alternative models
            error_msg = format_error_message(str(e))
            raise Exception(error_msg)
    
    def unload_model(self):
        """Unload the current model and free memory."""
        if self.model is None and self.generator is None:
            raise Exception("No model is currently loaded.")
        
        try:
            # Clear model references
            if self.model is not None:
                del self.model
            if self.tokenizer is not None:
                del self.tokenizer
            if self.generator is not None:
                del self.generator
            
            # Force garbage collection
            import gc
            gc.collect()
            
            # CPU-only: no CUDA cache to clear
            pass
            
            self.model = None
            self.tokenizer = None
            self.generator = None
            self.model_name = None
            
            logger.info("Model undeployed successfully")
            
        except Exception as e:
            logger.error(f"Error undeploying model: {str(e)}")
            raise Exception(f"Undeploy error: {str(e)}")
    
    def generate_response(self, prompt: str, max_length: int = 512, temperature: float = 0.7,
                          top_p: float = 0.9, top_k: int = 50, do_sample: bool = True,
                          num_return_sequences: int = 1) -> Dict[str, Any]:
        """Generate a response using the loaded model."""
        if self.generator is None:
            raise Exception("No model is currently loaded. Please deploy a model first.")
        
        if self.is_loading:
            raise Exception("Model is currently loading. Please wait.")
        
        try:
            start_time = time.time()
            
            # Standard approach for all models
            if self.model is None or self.tokenizer is None:
                raise Exception("Model or tokenizer not properly loaded.")
            
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt")
            input_tokens = inputs.input_ids.shape[1]
            
            # Generate response
            generation_kwargs = {
                "max_length": max_length,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "do_sample": do_sample,
                "num_return_sequences": num_return_sequences,
                "pad_token_id": self.tokenizer.eos_token_id,
            }
            
            # Generate using pipeline
            outputs = self.generator(prompt, **generation_kwargs)
            
            # Extract generated text
            generated_text = outputs[0]['generated_text']
            response_text = generated_text[len(prompt):].strip()
            
            # Count output tokens
            output_tokens = len(self.tokenizer.encode(response_text))
            
            generation_time = time.time() - start_time
            
            return {
                "response": response_text,
                "model_name": self.model_name,
                "generation_time": generation_time,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens
            }
            
        except Exception as e:
            logger.error(f"Error during generation: {str(e)}")
            raise Exception(f"Generation error: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the model."""
        device = "unknown"
        
        # Check if model is loaded
        is_loaded = self.model is not None or self.generator is not None
        
        if self.model is not None:
            if hasattr(self.model, 'device'):
                device = str(self.model.device)
            elif hasattr(self.model, 'hf_device_map'):
                device = str(self.model.hf_device_map)
        elif self.generator is not None:
            # For pipeline, check if it has device info
            if hasattr(self.generator, 'device'):
                device = str(self.generator.device)
            else:
                device = "cpu"  # Default
        
        return {
            "model_name": self.model_name,
            "is_loaded": is_loaded,
            "is_loading": self.is_loading,
            "device": device
        }
    
    def set_model_name(self, model_name: str):
        """Set the model name."""
        self.model_name = model_name
