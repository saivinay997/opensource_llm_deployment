#!/usr/bin/env python3
"""
Simple Client Example for Unified Model Deployment API
Demonstrates how to use the unified API for any model
"""

import requests
import json
import time
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"

def deploy_model(model_name: str) -> Dict[str, Any]:
    """Deploy a model."""
    print(f"🚀 Deploying {model_name}...")
    
    payload = {
        "model_name": model_name,
        "device": "cpu",
        "load_in_8bit": False,
        "load_in_4bit": False,
        "trust_remote_code": True
    }
    
    response = requests.post(f"{BASE_URL}/deploy", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
        return result
    else:
        print(f"❌ Error: {response.text}")
        return {}

def check_status() -> Dict[str, Any]:
    """Check model status."""
    print("📊 Checking model status...")
    
    response = requests.get(f"{BASE_URL}/status")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Model: {result.get('model_name', 'Unknown')}")
        print(f"   Loaded: {result.get('is_loaded', False)}")
        print(f"   Loading: {result.get('is_loading', False)}")
        print(f"   Device: {result.get('device', 'Unknown')}")
        return result
    else:
        print(f"❌ Error: {response.text}")
        return {}

def query_model(prompt: str, max_length: int = 256) -> Dict[str, Any]:
    """Query the model."""
    print(f"🤖 Querying model: {prompt[:50]}...")
    
    payload = {
        "prompt": prompt,
        "max_length": max_length,
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 50,
        "do_sample": True,
        "num_return_sequences": 1
    }
    
    response = requests.post(f"{BASE_URL}/query", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Response received in {result.get('generation_time', 0):.2f} seconds")
        return result
    else:
        print(f"❌ Error: {response.text}")
        return {}

def undeploy_model() -> Dict[str, Any]:
    """Undeploy the model."""
    print("🧹 Undeploying model...")
    
    response = requests.delete(f"{BASE_URL}/undeploy")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
        return result
    else:
        print(f"❌ Error: {response.text}")
        return {}

def wait_for_model_loading(max_wait_time: int = 300) -> bool:
    """Wait for model to finish loading."""
    print("⏳ Waiting for model to load...")
    
    start_time = time.time()
    while time.time() - start_time < max_wait_time:
        status = check_status()
        
        if status.get('is_loaded', False):
            print("✅ Model loaded successfully!")
            return True
        elif status.get('is_loading', False):
            print("⏳ Still loading...")
            time.sleep(10)
        else:
            print("❌ Model loading failed or stopped")
            return False
    
    print("⏰ Timeout waiting for model to load")
    return False

def main():
    """Main function demonstrating unified API usage."""
    print("🧪 Unified Model Deployment Client Example")
    print("=" * 50)
    
    # Test models
    test_models = [
        "gpt2",
        "microsoft/DialoGPT-medium",
        "facebook/opt-125m"
    ]
    
    test_prompts = [
        "Hello, how are you today?",
        "Explain artificial intelligence in simple terms:",
        "Write a short poem about technology:"
    ]
    
    try:
        for i, model_name in enumerate(test_models, 1):
            print(f"\n{'='*60}")
            print(f"🧪 Test {i}: {model_name}")
            print(f"{'='*60}")
            
            # Step 1: Deploy the model
            deploy_result = deploy_model(model_name)
            if not deploy_result:
                continue
            
            # Step 2: Wait for model to load
            if not wait_for_model_loading():
                continue
            
            # Step 3: Test queries
            for j, prompt in enumerate(test_prompts, 1):
                print(f"\n  🤖 Query {j}: {prompt}")
                print("-" * 40)
                
                result = query_model(prompt)
                if result:
                    print(f"  🤖 Response:")
                    print(f"  {result.get('response', 'No response')}")
                    print(f"\n  📊 Stats:")
                    print(f"     Generation time: {result.get('generation_time', 0):.2f}s")
                    print(f"     Input tokens: {result.get('input_tokens', 0)}")
                    print(f"     Output tokens: {result.get('output_tokens', 0)}")
            
            # Step 4: Clean up
            print(f"\n  🧹 Cleaning up {model_name}...")
            undeploy_model()
            
            print(f"\n  ✅ Test {i} completed successfully!")
        
        print("\n🎉 All tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
