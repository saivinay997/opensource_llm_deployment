#!/usr/bin/env python3
"""
Test script for the Open Source LLM Deployment Service

This script tests all the API endpoints to ensure they work correctly.
"""

import requests
import json
import time
import sys
from typing import Dict, Any

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_root_endpoint(self) -> bool:
        """Test the root endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                print("✅ Root endpoint test passed")
                print(f"   Service: {data.get('service')}")
                print(f"   Version: {data.get('version')}")
                return True
            else:
                print(f"❌ Root endpoint test failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Root endpoint test failed: {e}")
            return False
    
    def test_status_endpoint(self) -> bool:
        """Test the status endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/status")
            if response.status_code == 200:
                data = response.json()
                print("✅ Status endpoint test passed")
                print(f"   Model loaded: {data.get('is_loaded')}")
                print(f"   Model loading: {data.get('is_loading')}")
                return True
            else:
                print(f"❌ Status endpoint test failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Status endpoint test failed: {e}")
            return False
    
    def test_deploy_endpoint(self, model_name: str = "microsoft/DialoGPT-medium") -> bool:
        """Test the deploy endpoint."""
        try:
            payload = {
                "model_name": model_name,
                "device": "auto",
                "load_in_8bit": False,
                "trust_remote_code": True
            }
            
            response = self.session.post(f"{self.base_url}/deploy", json=payload)
            if response.status_code == 200:
                data = response.json()
                print("✅ Deploy endpoint test passed")
                print(f"   Message: {data.get('message')}")
                print(f"   Model: {data.get('model_name')}")
                print(f"   Device: {data.get('device')}")
                return True
            else:
                print(f"❌ Deploy endpoint test failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Deploy endpoint test failed: {e}")
            return False
    
    def wait_for_model_ready(self, timeout: int = 300) -> bool:
        """Wait for the model to be ready."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.session.get(f"{self.base_url}/status")
                if response.status_code == 200:
                    data = response.json()
                    if data["is_loaded"] and not data["is_loading"]:
                        print("✅ Model is ready!")
                        return True
                    elif data["is_loading"]:
                        print(f"⏳ Model is loading... ({data.get('model_name', 'Unknown')})")
                        time.sleep(5)
                    else:
                        print("❌ No model is loaded")
                        return False
                else:
                    print(f"❌ Status check failed: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ Status check failed: {e}")
                return False
        
        print("❌ Model loading timeout")
        return False
    
    def test_query_endpoint(self) -> bool:
        """Test the query endpoint."""
        try:
            payload = {
                "prompt": "Hello, how are you?",
                "max_length": 100,
                "temperature": 0.7
            }
            
            response = self.session.post(f"{self.base_url}/query", json=payload)
            if response.status_code == 200:
                data = response.json()
                print("✅ Query endpoint test passed")
                print(f"   Response: {data.get('response')}")
                print(f"   Generation time: {data.get('generation_time'):.2f}s")
                print(f"   Input tokens: {data.get('input_tokens')}")
                print(f"   Output tokens: {data.get('output_tokens')}")
                return True
            else:
                print(f"❌ Query endpoint test failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Query endpoint test failed: {e}")
            return False
    
    def test_undeploy_endpoint(self) -> bool:
        """Test the undeploy endpoint."""
        try:
            response = self.session.delete(f"{self.base_url}/undeploy")
            if response.status_code == 200:
                data = response.json()
                print("✅ Undeploy endpoint test passed")
                print(f"   Message: {data.get('message')}")
                return True
            else:
                print(f"❌ Undeploy endpoint test failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Undeploy endpoint test failed: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all API tests."""
        print("🚀 Starting API Tests")
        print("=" * 50)
        
        tests = [
            ("Root Endpoint", self.test_root_endpoint),
            ("Status Endpoint", self.test_status_endpoint),
            ("Deploy Endpoint", lambda: self.test_deploy_endpoint()),
            ("Model Loading", self.wait_for_model_ready),
            ("Query Endpoint", self.test_query_endpoint),
            ("Undeploy Endpoint", self.test_undeploy_endpoint),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📋 Testing: {test_name}")
            print("-" * 30)
            
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed!")
            return True
        else:
            print("❌ Some tests failed!")
            return False

def main():
    """Main function to run the tests."""
    # Check if service is running
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code != 200:
            print("❌ Service is not running or not responding correctly")
            print("Please start the service with: python main.py")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to the service")
        print("Please start the service with: python main.py")
        sys.exit(1)
    
    # Run tests
    tester = APITester()
    success = tester.run_all_tests()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
