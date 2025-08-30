#!/usr/bin/env python3
"""
Basic setup test - tests imports without transformers
"""

import sys
import os

def test_basic_imports():
    """Test basic imports that should work."""
    print("🧪 Testing basic imports...")
    
    try:
        import fastapi
        print(f"✅ FastAPI version: {fastapi.__version__}")
    except Exception as e:
        print(f"❌ FastAPI import failed: {e}")
    
    try:
        import uvicorn
        print(f"✅ Uvicorn imported successfully")
    except Exception as e:
        print(f"❌ Uvicorn import failed: {e}")
    
    try:
        import pydantic
        print(f"✅ Pydantic version: {pydantic.__version__}")
    except Exception as e:
        print(f"❌ Pydantic import failed: {e}")
    
    try:
        import requests
        print(f"✅ Requests imported successfully")
    except Exception as e:
        print(f"❌ Requests import failed: {e}")
    
    try:
        import numpy
        print(f"✅ NumPy version: {numpy.__version__}")
    except Exception as e:
        print(f"❌ NumPy import failed: {e}")

def test_pytorch_import():
    """Test PyTorch import specifically."""
    print("\n🧪 Testing PyTorch import...")
    
    try:
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")
        print(f"✅ CUDA available: {torch.cuda.is_available()}")
        print(f"✅ Device count: {torch.cuda.device_count() if torch.cuda.is_available() else 0}")
    except Exception as e:
        print(f"❌ PyTorch import failed: {e}")
        print("💡 This indicates a PyTorch installation issue")

def test_transformers_import():
    """Test transformers import specifically."""
    print("\n🧪 Testing Transformers import...")
    
    try:
        import transformers
        print(f"✅ Transformers version: {transformers.__version__}")
    except Exception as e:
        print(f"❌ Transformers import failed: {e}")
        print("💡 This indicates a transformers installation issue")

def main():
    """Run all tests."""
    print("🚀 Basic Setup Test Suite")
    print("=" * 60)
    
    test_basic_imports()
    test_pytorch_import()
    test_transformers_import()
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print("• If PyTorch fails: Run 'python fix_pytorch_compatibility.py'")
    print("• If Transformers fails: Check version compatibility")
    print("• If basic imports fail: Check your Python environment")

if __name__ == "__main__":
    main()
