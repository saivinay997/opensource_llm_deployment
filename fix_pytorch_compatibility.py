#!/usr/bin/env python3
"""
Fix PyTorch compatibility issues
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a command and return the result."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    """Fix PyTorch compatibility issues."""
    print("🔧 Fixing PyTorch compatibility issues...")
    print("=" * 60)
    
    # Step 1: Upgrade transformers to latest version
    print("📦 Upgrading transformers...")
    success, stdout, stderr = run_command("pip install --upgrade transformers")
    if success:
        print("✅ Transformers upgraded successfully")
    else:
        print(f"❌ Failed to upgrade transformers: {stderr}")
    
    # Step 2: Upgrade PyTorch to latest compatible version
    print("📦 Upgrading PyTorch...")
    success, stdout, stderr = run_command("pip install --upgrade torch")
    if success:
        print("✅ PyTorch upgraded successfully")
    else:
        print(f"❌ Failed to upgrade PyTorch: {stderr}")
    
    # Step 3: Install specific compatible versions if needed
    print("📦 Installing compatible versions...")
    commands = [
        "pip install torch==2.1.2",
        "pip install transformers==4.36.0",
        "pip install accelerate==0.24.1"
    ]
    
    for cmd in commands:
        success, stdout, stderr = run_command(cmd)
        if success:
            print(f"✅ {cmd.split('==')[0]} installed successfully")
        else:
            print(f"❌ Failed to install {cmd.split('==')[0]}: {stderr}")
    
    # Step 4: Test import
    print("🧪 Testing imports...")
    try:
        import torch
        import transformers
        print(f"✅ PyTorch version: {torch.__version__}")
        print(f"✅ Transformers version: {transformers.__version__}")
        print("✅ All imports successful!")
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False
    
    print("\n🎉 PyTorch compatibility fix completed!")
    print("💡 You can now run your LLM service without compatibility issues.")
    return True

if __name__ == "__main__":
    main()
