#!/usr/bin/env python3
"""
Memory Check Script for Large Model Deployment
Checks system resources and provides recommendations for model deployment
"""

import sys
from utils import check_system_resources, get_model_recommendations, is_large_model

def main():
    """Main function for memory check."""
    print("🔍 System Resource Check")
    print("=" * 50)
    
    # Check system resources
    resources = check_system_resources()
    
    if not resources:
        print("❌ Error: Could not check system resources")
        return
    
    # Display memory status
    memory = resources["memory"]
    print(f"📊 Memory Status:")
    print(f"   Total RAM: {memory['total_gb']:.1f} GB")
    print(f"   Available: {memory['available_gb']:.1f} GB")
    print(f"   Used: {memory['used_gb']:.1f} GB ({memory['percent']:.1f}%)")
    
    # Display CPU status
    cpu = resources["cpu"]
    print(f"\n🖥️  CPU Status:")
    print(f"   Cores: {cpu['cores']}")
    print(f"   Usage: {cpu['usage_percent']:.1f}%")
    
    # Display disk status
    disk = resources["disk"]
    print(f"\n💾 Disk Status:")
    print(f"   Total: {disk['total_gb']:.1f} GB")
    print(f"   Free: {disk['free_gb']:.1f} GB")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    
    if memory['total_gb'] < 16:
        print("   ❌ Insufficient RAM for large models")
        print("   💡 Recommended models: gpt2, distilgpt2, microsoft/DialoGPT-medium")
    elif memory['total_gb'] < 32:
        print("   ⚠️  Limited RAM for 20B models")
        print("   💡 Consider smaller models or ensure no other processes running")
        print("   💡 Recommended: microsoft/DialoGPT-medium, gpt2")
    else:
        print("   ✅ Sufficient RAM for large models")
        print("   💡 You can try facebook/opt-1.3b or other large models")
    
    if disk['free_gb'] < 50:
        print("   ⚠️  Limited disk space for model caching")
        print("   💡 Clear some space or use smaller models")
    
    # Get model recommendations
    recommendations = get_model_recommendations(memory['available_gb'])
    print(f"\n🚀 Recommended Models for {memory['available_gb']:.1f}GB RAM:")
    for model in recommendations:
        print(f"   • {model}")
    
    print(f"\n🚀 Model Recommendations by RAM:")
    print(f"   < 8GB:  gpt2, distilgpt2")
    print(f"   8-16GB: microsoft/DialoGPT-medium, EleutherAI/gpt-neo-125M")
    print(f"   16-32GB: facebook/opt-350m, microsoft/DialoGPT-large")
    print(f"   > 32GB: facebook/opt-1.3b, other large models")

def check_model_requirements(model_name):
    """Check specific requirements for a model."""
    print(f"\n🎯 Model Requirements Check: {model_name}")
    print("=" * 50)
    
    if is_large_model(model_name):
        print("⚠️  Large Model Detected!")
        print("   • Requires 32GB+ RAM")
        print("   • CPU-only deployment recommended")
        print("   • May take 10-30 minutes to load")
        print("   • Consider using smaller models for testing")
    elif "7b" in model_name.lower():
        print("⚠️  Medium-Large Model")
        print("   • Requires 16GB+ RAM")
        print("   • CPU deployment possible")
    else:
        print("✅ Standard Model")
        print("   • Should work on most systems")
        print("   • 4-8GB RAM sufficient")

if __name__ == "__main__":
    main()
    
    if len(sys.argv) > 1:
        model_name = sys.argv[1]
        check_model_requirements(model_name)
    else:
        print(f"\n💡 Usage: python memory_check.py <model_name>")
        print(f"   Example: python memory_check.py facebook/opt-1.3b")
