#!/usr/bin/env python3
"""
Test script to verify the fixes for truncation, max_new_tokens, and dtype issues
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_model_deployment():
    """Test model deployment with a small model."""
    print("Testing model deployment...")
    
    # Use a small model for testing
    deploy_data = {
        "model_name": "microsoft/DialoGPT-small",  # Small model for testing
        "device": "cpu",
        "load_in_8bit": False,
        "load_in_4bit": False,
        "trust_remote_code": True,
        "hf_token": None
    }
    
    try:
        response = requests.post(f"{BASE_URL}/deploy", json=deploy_data)
        print(f"Deploy response: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Wait for model to load
        time.sleep(10)
        
        return response.status_code == 200
    except Exception as e:
        print(f"Deploy error: {e}")
        return False

def test_model_status():
    """Test getting model status."""
    print("\nTesting model status...")
    
    try:
        response = requests.get(f"{BASE_URL}/status")
        print(f"Status response: {response.status_code}")
        print(f"Status: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Status error: {e}")
        return False

def test_generation():
    """Test text generation with the fixes."""
    print("\nTesting text generation...")
    
    # Test with max_length only
    query_data_1 = {
        "prompt": "Hello, how are you?",
        "max_length": 100,
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 50,
        "do_sample": True,
        "num_return_sequences": 1
    }
    
    # Test with max_new_tokens
    query_data_2 = {
        "prompt": "The weather is nice today.",
        "max_new_tokens": 50,
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 50,
        "do_sample": True,
        "num_return_sequences": 1
    }
    
    try:
        print("Testing with max_length...")
        response1 = requests.post(f"{BASE_URL}/query", json=query_data_1)
        print(f"Query 1 response: {response1.status_code}")
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"Generated text: {result1['response']}")
            print(f"Generation time: {result1['generation_time']:.2f}s")
        else:
            print(f"Error: {response1.text}")
        
        print("\nTesting with max_new_tokens...")
        response2 = requests.post(f"{BASE_URL}/query", json=query_data_2)
        print(f"Query 2 response: {response2.status_code}")
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"Generated text: {result2['response']}")
            print(f"Generation time: {result2['generation_time']:.2f}s")
        else:
            print(f"Error: {response2.text}")
        
        return response1.status_code == 200 and response2.status_code == 200
    except Exception as e:
        print(f"Generation error: {e}")
        return False

def test_model_undeploy():
    """Test model undeployment."""
    print("\nTesting model undeployment...")
    
    try:
        response = requests.delete(f"{BASE_URL}/undeploy")
        print(f"Undeploy response: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Undeploy error: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing LLM Deployment Fixes")
    print("=" * 40)
    
    # Test deployment
    deploy_success = test_model_deployment()
    
    if deploy_success:
        # Test status
        status_success = test_model_status()
        
        # Test generation
        generation_success = test_generation()
        
        # Test undeployment
        undeploy_success = test_model_undeploy()
        
        print("\n" + "=" * 40)
        print("Test Results:")
        print(f"Deployment: {'✓' if deploy_success else '✗'}")
        print(f"Status: {'✓' if status_success else '✗'}")
        print(f"Generation: {'✓' if generation_success else '✗'}")
        print(f"Undeployment: {'✓' if undeploy_success else '✗'}")
        
        if all([deploy_success, status_success, generation_success, undeploy_success]):
            print("\n🎉 All tests passed! The fixes are working correctly.")
        else:
            print("\n❌ Some tests failed. Check the logs above for details.")
    else:
        print("\n❌ Deployment failed. Cannot run other tests.")

if __name__ == "__main__":
    main()
