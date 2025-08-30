#!/usr/bin/env python3
"""
Client example for the Open Source LLM Deployment Service

This script demonstrates how to use the FastAPI service to deploy and query LLMs.
"""

import requests
import json
import time
from typing import Dict, Any

class LLMServiceClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def deploy_model(self, model_name: str, **kwargs) -> Dict[str, Any]:
        """Deploy a model from Hugging Face (CPU-only)."""
        payload = {
            "model_name": model_name,
            "device": kwargs.get("device", "cpu"),  # Default to CPU for VM compatibility
            "load_in_8bit": False,  # Disabled for CPU-only
            "load_in_4bit": False,  # Disabled for CPU-only
            "trust_remote_code": kwargs.get("trust_remote_code", True),
            "hf_token": kwargs.get("hf_token", None)
        }
        
        response = self.session.post(f"{self.base_url}/deploy", json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current model status."""
        response = self.session.get(f"{self.base_url}/status")
        response.raise_for_status()
        return response.json()
    
    def wait_for_model_ready(self, timeout: int = 300) -> bool:
        """Wait for the model to be ready."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_status()
            if status["is_loaded"] and not status["is_loading"]:
                return True
            elif status["is_loading"]:
                print(f"Model is loading... ({status.get('model_name', 'Unknown')})")
                time.sleep(5)
            else:
                print("No model is loaded.")
                return False
        return False
    
    def query_model(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Query the deployed model."""
        payload = {
            "prompt": prompt,
            "max_length": kwargs.get("max_length", 512),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 0.9),
            "top_k": kwargs.get("top_k", 50),
            "do_sample": kwargs.get("do_sample", True),
            "num_return_sequences": kwargs.get("num_return_sequences", 1)
        }
        
        response = self.session.post(f"{self.base_url}/query", json=payload)
        response.raise_for_status()
        return response.json()
    
    def undeploy_model(self) -> Dict[str, Any]:
        """Undeploy the current model."""
        response = self.session.delete(f"{self.base_url}/undeploy")
        response.raise_for_status()
        return response.json()

def main():
    """Main function demonstrating the client usage."""
    client = LLMServiceClient()
    
    print("🚀 Open Source LLM Deployment Service Client")
    print("=" * 50)
    
    # Example 1: Deploy a small model (DialoGPT-medium)
    print("\n1. Deploying DialoGPT-medium model...")
    try:
        deploy_response = client.deploy_model("microsoft/DialoGPT-medium")
        print(f"✅ Deploy response: {deploy_response}")
        
        # Wait for model to be ready
        if client.wait_for_model_ready():
            print("✅ Model is ready!")
            
            # Query the model
            print("\n2. Querying the model...")
            query_response = client.query_model(
                "Hello, how are you today?",
                max_length=100,
                temperature=0.8
            )
            print(f"✅ Query response:")
            print(f"   Response: {query_response['response']}")
            print(f"   Generation time: {query_response['generation_time']:.2f}s")
            print(f"   Input tokens: {query_response['input_tokens']}")
            print(f"   Output tokens: {query_response['output_tokens']}")
            
            # Undeploy the model
            print("\n3. Undeploying the model...")
            undeploy_response = client.undeploy_model()
            print(f"✅ Undeploy response: {undeploy_response}")
            
        else:
            print("❌ Model failed to load within timeout")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
    
    # Example 2: Deploy with quantization (if you have enough memory)
    print("\n" + "=" * 50)
    print("4. Example with quantization (commented out - uncomment to try)")
    
    """
    # Uncomment this section to try quantization
    try:
        print("Deploying model with 8-bit quantization...")
        deploy_response = client.deploy_model(
            "microsoft/DialoGPT-medium",
            load_in_8bit=True
        )
        print(f"✅ Deploy response: {deploy_response}")
        
        if client.wait_for_model_ready():
            print("✅ Model is ready!")
            
            # Multiple queries
            prompts = [
                "What is artificial intelligence?",
                "Tell me a joke",
                "Explain quantum computing"
            ]
            
            for i, prompt in enumerate(prompts, 1):
                print(f"\nQuery {i}: {prompt}")
                response = client.query_model(prompt, max_length=150)
                print(f"Response: {response['response']}")
            
            client.undeploy_model()
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
    """
    
    print("\n" + "=" * 50)
    print("🎉 Client example completed!")

def interactive_mode():
    """Interactive mode for testing the service."""
    client = LLMServiceClient()
    
    print("🔧 Interactive Mode")
    print("Commands:")
    print("  deploy <model_name> - Deploy a model")
    print("  status - Check model status")
    print("  query <prompt> - Query the model")
    print("  undeploy - Undeploy the model")
    print("  quit - Exit")
    print("=" * 50)
    
    while True:
        try:
            command = input("\n> ").strip().split()
            if not command:
                continue
                
            cmd = command[0].lower()
            
            if cmd == "quit":
                break
            elif cmd == "deploy" and len(command) > 1:
                model_name = command[1]
                print(f"Deploying {model_name}...")
                response = client.deploy_model(model_name)
                print(f"Response: {response}")
            elif cmd == "status":
                response = client.get_status()
                print(f"Status: {response}")
            elif cmd == "query" and len(command) > 1:
                prompt = " ".join(command[1:])
                print(f"Querying: {prompt}")
                response = client.query_model(prompt)
                print(f"Response: {response['response']}")
            elif cmd == "undeploy":
                response = client.undeploy_model()
                print(f"Response: {response}")
            else:
                print("Invalid command. Use 'quit' to exit.")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        main()
