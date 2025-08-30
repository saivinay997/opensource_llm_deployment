# 🚀 GPT-OSS-20B Deployment Guide

This guide provides step-by-step instructions for deploying the `openai/gpt-oss-20b` model on your CPU-only VM.

## 📋 Prerequisites

### System Requirements
- **RAM**: Minimum 32GB (64GB recommended)
- **Storage**: At least 100GB free space
- **CPU**: Multi-core processor (8+ cores recommended)
- **Network**: Stable internet connection for model download

### Check Your System
```bash
# Run the memory check script
python memory_check.py openai/gpt-oss-20b

# Or check manually
free -h
df -h
nproc
```

## 🔧 Deployment Steps

### 1. Update the Service
```bash
# Navigate to your project directory
cd ~/opensource_llm_deployment

# Stop current service
docker-compose down

# Rebuild with latest changes
docker-compose build --no-cache

# Start the service
docker-compose up -d
```

### 2. Deploy GPT-OSS-20B

#### Option A: Using Web Interface
1. Open: `http://40.81.226.13:8000/web-interface`
2. Click on "GPT-OSS-20B" preset
3. Leave HF Token empty (if you have access)
4. Set Device to "CPU"
5. Click "Deploy Model"

#### Option B: Using API
```bash
curl -X POST "http://40.81.226.13:8000/deploy" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "openai/gpt-oss-20b",
    "device": "cpu",
    "load_in_8bit": false,
    "load_in_4bit": false,
    "trust_remote_code": true
  }'
```

#### Option C: Using Python Client
```python
from client_example import LLMServiceClient

client = LLMServiceClient("http://40.81.226.13:8000")

# Deploy the model
response = client.deploy_model(
    model_name="openai/gpt-oss-20b",
    device="cpu"
)
print(response)
```

### 3. Monitor Deployment
```bash
# Check deployment status
curl http://40.81.226.13:8000/status

# Monitor logs
docker-compose logs -f

# Check memory usage
docker stats
```

## ⏱️ Expected Timeline

- **Model Download**: 15-30 minutes (depending on network)
- **Model Loading**: 10-20 minutes (depending on CPU/RAM)
- **Total Time**: 25-50 minutes

## 🧪 Testing the Model

### 1. Check Status
```bash
curl http://40.81.226.13:8000/status
```

### 2. Test Query
```bash
curl -X POST "http://40.81.226.13:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing in simple terms:",
    "max_length": 200,
    "temperature": 0.7
  }'
```

### 3. Web Interface Test
1. Go to: `http://40.81.226.13:8000/web-interface`
2. Enter a prompt like: "Write a short story about a robot learning to paint"
3. Click "Generate Response"

## 🔍 Troubleshooting

### Memory Issues
```bash
# Check available memory
free -h

# Kill unnecessary processes
sudo pkill -f "unnecessary_process"

# Restart with more memory
docker-compose down
docker-compose up -d
```

### Slow Loading
- The model is 20B parameters - loading takes time
- Monitor with: `docker-compose logs -f`
- Be patient - this is normal for large models

### Model Access Issues
If you get access errors:
1. Get a Hugging Face token from: https://huggingface.co/settings/tokens
2. Add the token to your deployment request
3. Ensure you have access to the model repository

### Alternative Models
If GPT-OSS-20B fails, try these alternatives:
- `microsoft/DialoGPT-medium` (recommended for testing)
- `gpt2` (very reliable)
- `distilgpt2` (smaller, faster)

## 📊 Performance Tips

### For Better Performance
1. **Close other applications** to free up RAM
2. **Use shorter prompts** initially
3. **Start with lower max_length** (100-200)
4. **Monitor system resources** during generation

### Memory Optimization
```bash
# Clear Docker cache
docker system prune -a

# Monitor memory usage
watch -n 1 'free -h'

# Check if model is loaded
curl http://40.81.226.13:8000/status
```

## 🎯 Example Prompts

### Creative Writing
```
"Write a short story about a time traveler who discovers they can only travel to the past:"
```

### Technical Explanation
```
"Explain how machine learning works in simple terms:"
```

### Code Generation
```
"Write a Python function to calculate the fibonacci sequence:"
```

### Conversation
```
"Hello! How are you today? Can you tell me about your capabilities?"
```

## 🚨 Important Notes

1. **First Load**: The model will download (~40GB) on first use
2. **Memory Usage**: Expect 30-40GB RAM usage when loaded
3. **Generation Time**: Responses may take 10-30 seconds
4. **CPU Usage**: High CPU usage during generation is normal
5. **Persistence**: Model stays loaded until you undeploy it

## 🔄 Undeploying

When you're done:
```bash
# Undeploy to free memory
curl -X DELETE http://40.81.226.13:8000/undeploy

# Or use web interface
# Click "Undeploy Model" button
```

## 📞 Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Run memory check: `python memory_check.py openai/gpt-oss-20b`
3. Try a smaller model first to test the system
4. Ensure you have sufficient RAM and disk space

---

**Happy deploying! 🎉**
