# Troubleshooting Guide

## Common Issues and Solutions

### 1. Gated Repository Access Error

**Error**: `OSError: You are trying to access a gated repo.`

**Solution**:
1. **Get a Hugging Face Token**:
   ```bash
   # Go to https://huggingface.co/settings/tokens
   # Create a new token
   ```

2. **Login via CLI**:
   ```bash
   pip install huggingface_hub
   huggingface-cli login
   # Enter your token when prompted
   ```

3. **Request Model Access**:
   - Visit the model page (e.g., https://huggingface.co/google/gemma-2b)
   - Click "Request access"
   - Follow the instructions

4. **Use Public Models Instead**:
   ```json
   {
     "model_name": "microsoft/DialoGPT-medium",
     "device": "auto"
   }
   ```

### 2. Out of Memory (OOM) Error

**Error**: `RuntimeError: CUDA out of memory` or `RuntimeError: out of memory`

**Solutions**:
1. **Use Smaller Models**:
   - `microsoft/DialoGPT-small` (117M parameters)
   - `distilgpt2` (82M parameters)
   - `gpt2` (124M parameters)

2. **Monitor RAM Usage**:
   ```bash
   # Check available memory
   free -h
   ```

3. **Use CPU-Optimized Models**:
   ```json
   {
     "model_name": "microsoft/DialoGPT-medium",
     "device": "cpu"
   }
   ```

### 2.1. Quantization Dependencies Error

**Error**: `ImportError: Using load_in_8bit=True requires Accelerate`

**Solutions**:
1. **Install Missing Dependencies**:
   ```bash
   pip install accelerate bitsandbytes
   ```

2. **Use Full Precision** (if quantization fails):
   ```json
   {
     "model_name": "microsoft/DialoGPT-medium",
     "load_in_8bit": false,
     "load_in_4bit": false
   }
   ```

3. **Install from Test PyPI** (if regular install fails):
   ```bash
   pip install -i https://test.pypi.org/simple/ bitsandbytes
   ```

### 3. Model Loading Errors

**Error**: `OSError: We couldn't connect to 'https://huggingface.co'`

**Solutions**:
1. **Check Internet Connection**
2. **Use Proxy if needed**:
   ```bash
   export HTTPS_PROXY="http://your-proxy:port"
   ```

3. **Clear Cache**:
   ```bash
   rm -rf ~/.cache/huggingface/
   ```

### 4. CPU Performance Issues

**Issue**: Slow inference on CPU

**Solutions**:
1. **Use Smaller Models**:
   - Models under 1B parameters work best on CPU
   - Consider `distilgpt2` or `microsoft/DialoGPT-small`

2. **Monitor System Resources**:
   ```bash
   # Check CPU usage
   top
   # Check memory usage
   free -h
   ```

3. **Optimize Model Settings**:
   ```json
   {
     "model_name": "microsoft/DialoGPT-medium",
     "device": "cpu"
   }
   ```

### 5. Model Not Found

**Error**: `OSError: Couldn't reach https://huggingface.co/model-name`

**Solutions**:
1. **Check Model Name**: Ensure the model exists on Hugging Face
2. **Use Correct Model ID**: Check the exact model name on the Hugging Face page
3. **Try Alternative Models**:
   ```json
   {
     "model_name": "microsoft/DialoGPT-medium"
   }
   ```

### 6. Permission Denied

**Error**: `PermissionError: [Errno 13] Permission denied`

**Solutions**:
1. **Check File Permissions**:
   ```bash
   chmod -R 755 ~/.cache/huggingface/
   ```

2. **Run with Appropriate Permissions**:
   ```bash
   sudo python main.py  # Not recommended for production
   ```

### 7. Slow Model Loading

**Issue**: Models take too long to load

**Solutions**:
1. **Use Quantization**:
   ```json
   {
     "model_name": "microsoft/DialoGPT-medium",
     "load_in_8bit": true
   }
   ```

2. **Use SSD Storage**: Ensure models are cached on fast storage
3. **Use Smaller Models**: Start with smaller models for testing

### 8. API Connection Issues

**Error**: `ConnectionError: HTTPConnectionPool`

**Solutions**:
1. **Check Service Status**:
   ```bash
   curl http://localhost:8000/
   ```

2. **Restart Service**:
   ```bash
   python main.py
   ```

3. **Check Port Availability**:
   ```bash
   netstat -tulpn | grep :8000
   ```

### 9. Uvicorn Reload Warning

**Warning**: `You must pass the application as an import string to enable 'reload' or 'workers'`

**Solutions**:
1. **For Production (No Reload)**:
   ```bash
   python main.py
   ```

2. **For Development (With Reload)**:
   ```bash
   python run_dev.py
   # or
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Quick Fixes

### For Immediate Testing

Use this simple configuration to test the service:

```bash
# 1. Start the service
python main.py

# 2. Deploy a small public model
curl -X POST "http://localhost:8000/deploy" \
     -H "Content-Type: application/json" \
     -d '{
       "model_name": "microsoft/DialoGPT-medium",
       "device": "cpu"
     }'

# 3. Query the model
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "Hello, how are you?",
       "max_length": 50
     }'
```

### Environment Setup

```bash
# Create virtual environment
conda create -n llm-deployment python=3.9
conda activate llm-deployment

# Install dependencies
pip install -r requirements.txt

# Test installation
python -c "import torch; print('PyTorch:', torch.__version__); print('CPU available:', torch.cuda.is_available() == False)"
```

## Getting Help

If you're still experiencing issues:

1. **Check Logs**: Look at the console output for detailed error messages
2. **Test with Simple Model**: Try with `microsoft/DialoGPT-medium` first
3. **Check System Requirements**: Ensure you have sufficient RAM and storage
4. **Update Dependencies**: Make sure all packages are up to date

## Recommended Models for Testing

### **Beginner-Friendly (No Authentication)**
- `microsoft/DialoGPT-medium` - Good for conversation
- `distilgpt2` - Fast and small
- `gpt2` - Classic GPT-2 model

### **For Production (May Require Authentication)**
- `meta-llama/Llama-2-7b-chat-hf` - High quality responses
- `mistralai/Mistral-7B-Instruct-v0.2` - Good instruction following
- `google/gemma-2b` - Efficient and capable
