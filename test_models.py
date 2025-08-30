#!/usr/bin/env python3
"""
Test script to verify model compatibility
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model_manager import ModelManager
from utils import is_large_model, format_error_message

def test_model_compatibility(model_name: str):
    """Test if a model can be loaded successfully."""
    print(f"🧪 Testing model: {model_name}")
    print("=" * 60)
    
    manager = ModelManager()
    
    try:
        # Try to load the model
        manager.load_model_sync(
            model_name=model_name,
            device="cpu",
            load_in_8bit=False,
            load_in_4bit=False,
            trust_remote_code=True
        )
        
        print(f"✅ SUCCESS: {model_name} loaded successfully!")
        
        # Test a simple generation
        try:
            result = manager.generate_response(
                prompt="Hello, how are you?",
                max_length=50,
                temperature=0.7
            )
            print(f"✅ Generation test passed!")
            print(f"Response: {result['response'][:100]}...")
        except Exception as e:
            print(f"⚠️  Generation failed: {e}")
        
        # Clean up
        manager.unload_model()
        print(f"✅ Model unloaded successfully")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        formatted_error = format_error_message(str(e))
        print(f"💡 Suggestions: {formatted_error}")
    
    print("\n" + "=" * 60 + "\n")

def main():
    """Test multiple models for compatibility."""
    print("🚀 Model Compatibility Test Suite")
    print("=" * 60)
    
    # Test models in order of reliability
    test_models = [
        "gpt2",  # Most reliable
        "distilgpt2",  # Smaller, faster
        "microsoft/DialoGPT-medium",  # Good for testing
        "EleutherAI/gpt-neo-125M",  # Alternative
        "facebook/opt-125m",  # Another option
    ]
    
    for model in test_models:
        test_model_compatibility(model)
    
    print("🎯 Summary:")
    print("• gpt2 and distilgpt2 are the most reliable")
    print("• microsoft/DialoGPT-medium is good for testing")
    print("• Try the recommended models first!")

if __name__ == "__main__":
    main()
