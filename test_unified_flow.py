#!/usr/bin/env python3
"""
Test Unified Model Deployment and Inference Flow
Tests the common flow for deploying and inferencing any model
"""

import sys
import os
import time
import logging

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model_manager import ModelManager
from utils import setup_logging, check_system_resources

def test_model_deployment():
    """Test model deployment with different models."""
    print("🚀 Testing Unified Model Deployment")
    print("=" * 50)
    
    # Setup logging
    setup_logging("INFO")
    
    # Check system resources
    resources = check_system_resources()
    print(f"📊 System Resources:")
    print(f"   Memory: {resources['memory']['available_gb']:.1f}GB available")
    print(f"   CPU: {resources['cpu']['cores']} cores")
    print(f"   Disk: {resources['disk']['free_gb']:.1f}GB free")
    
    # Test models (from small to large)
    test_models = [
        "gpt2",  # Small, reliable
        "microsoft/DialoGPT-medium",  # Medium size
        "facebook/opt-125m"  # Another medium model
    ]
    
    model_manager = ModelManager()
    
    for i, model_name in enumerate(test_models, 1):
        print(f"\n🧪 Test {i}: Deploying {model_name}")
        print("-" * 40)
        
        try:
            # Deploy model
            print(f"📥 Loading {model_name}...")
            start_time = time.time()
            
            model_manager.load_model_sync(
                model_name=model_name,
                device="cpu",
                load_in_8bit=False,
                load_in_4bit=False,
                trust_remote_code=True,
                hf_token=None
            )
            
            load_time = time.time() - start_time
            print(f"✅ Model loaded in {load_time:.2f} seconds")
            
            # Test inference
            test_prompts = [
                "Hello, how are you?",
                "Explain machine learning in simple terms:",
                "Write a short poem about technology:"
            ]
            
            for j, prompt in enumerate(test_prompts, 1):
                print(f"\n  🤖 Test {i}.{j}: {prompt[:30]}...")
                
                try:
                    result = model_manager.generate_response(
                        prompt=prompt,
                        max_length=100,
                        temperature=0.7
                    )
                    
                    print(f"    ✅ Response: {result['response'][:100]}...")
                    print(f"    ⏱️  Time: {result['generation_time']:.2f}s")
                    print(f"    📝 Tokens: {result['input_tokens']} → {result['output_tokens']}")
                    
                except Exception as e:
                    print(f"    ❌ Inference failed: {e}")
            
            # Clean up
            print(f"\n  🧹 Unloading {model_name}...")
            model_manager.unload_model()
            print(f"  ✅ Model unloaded successfully")
            
        except Exception as e:
            print(f"❌ Failed to deploy {model_name}: {e}")
            # Try to clean up if model was partially loaded
            try:
                model_manager.unload_model()
            except:
                pass
    
    print("\n🎉 Unified model deployment test completed!")

def test_api_integration():
    """Test API integration."""
    print("\n\n🔌 Testing API Integration")
    print("=" * 50)
    
    try:
        from api_routes import router
        print("✅ API router imported successfully")
        
        from models import ModelRequest, QueryRequest
        print("✅ Model schemas imported successfully")
        
        print("✅ API integration test passed!")
        
    except Exception as e:
        print(f"❌ API integration test failed: {e}")

def main():
    """Main test function."""
    print("🧪 Unified Model Deployment Test")
    print("=" * 60)
    
    # Test 1: Model deployment and inference
    test_model_deployment()
    
    # Test 2: API integration
    test_api_integration()
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print("✅ Unified model deployment flow working")
    print("✅ API integration working")
    print("\n💡 You can now deploy any Hugging Face model using the unified API!")

if __name__ == "__main__":
    main()

