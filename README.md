# Open Source LLM Deployment Service

A FastAPI-based service for deploying and hosting open-source Large Language Models from Hugging Face. This service provides a RESTful API to easily deploy, query, and manage LLMs optimized for CPU-only environments like VMs.

## Features

- 🚀 **Easy Model Deployment**: Deploy any open-source LLM from Hugging Face with a single API call
- 💻 **CPU-Optimized**: Designed specifically for VM environments with CPU-only processing
- 📊 **Real-time Monitoring**: Track model status, generation time, and token usage
- 🎯 **Production Ready**: Built with FastAPI for high performance and automatic API documentation
- 🔄 **Memory Management**: Proper model loading/unloading with memory cleanup
- 🌐 **CORS Support**: Ready for web applications

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd opensource_llm_deployment

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the Service

```bash
# Run the FastAPI server
python main.py
```

The service will be available at `http://localhost:8000`

### 3. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. Deploy Model
**POST** `/deploy`

Deploy a new model from Hugging Face.

```json
{
  "model_name": "microsoft/DialoGPT-medium",
  "device": "cpu",
  "load_in_8bit": false,
  "load_in_4bit": false,
  "trust_remote_code": true,
  "hf_token": "your_huggingface_token_here"
}
```

**Parameters:**
- `model_name` (required): Hugging Face model identifier
- `device` (optional): Device to load model on (defaults to "cpu" for VM compatibility)
- `load_in_8bit` (optional): Disabled for CPU-only environments
- `load_in_4bit` (optional): Disabled for CPU-only environments
- `trust_remote_code` (optional): Trust remote code from Hugging Face
- `hf_token` (optional): Hugging Face token for accessing gated models

### 2. Query Model
**POST** `/query`

Query the deployed model with text generation.

```json
{
  "prompt": "Hello, how are you?",
  "max_length": 512,
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 50,
  "do_sample": true,
  "num_return_sequences": 1
}
```

**Parameters:**
- `prompt` (required): Input text for generation
- `max_length` (optional): Maximum length of generated text
- `temperature` (optional): Sampling temperature (0.0-2.0)
- `top_p` (optional): Nucleus sampling parameter
- `top_k` (optional): Top-k sampling parameter
- `do_sample` (optional): Enable sampling vs greedy decoding
- `num_return_sequences` (optional): Number of sequences to generate

### 3. Get Model Status
**GET** `/status`

Get the current status of the deployed model.

### 4. Undeploy Model
**DELETE** `/undeploy`

Undeploy the current model and free memory.

## Usage Examples

### Python Client Example

```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

# 1. Deploy a model
deploy_response = requests.post(f"{BASE_URL}/deploy", json={
    "model_name": "microsoft/DialoGPT-medium",
    "device": "cpu"
})
print("Deploy response:", deploy_response.json())

# 2. Check model status
status_response = requests.get(f"{BASE_URL}/status")
print("Status:", status_response.json())

# 3. Query the model
query_response = requests.post(f"{BASE_URL}/query", json={
    "prompt": "Hello, how are you today?",
    "max_length": 100,
    "temperature": 0.8
})
print("Response:", query_response.json())

# 4. Undeploy the model
undeploy_response = requests.delete(f"{BASE_URL}/undeploy")
print("Undeploy response:", undeploy_response.json())
```

### cURL Examples

```bash
# Deploy a model
curl -X POST "http://localhost:8000/deploy" \
     -H "Content-Type: application/json" \
     -d '{
       "model_name": "microsoft/DialoGPT-medium",
       "device": "cpu"
     }'

# Query the model
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "Hello, how are you?",
       "max_length": 100,
       "temperature": 0.7
     }'

# Check status
curl -X GET "http://localhost:8000/status"

# Undeploy model
curl -X DELETE "http://localhost:8000/undeploy"
```

## Supported Models

This service supports any causal language model from Hugging Face, including:

### **Public Models (No Authentication Required)**
- **GPT Models**: microsoft/DialoGPT-medium, microsoft/DialoGPT-large
- **Code Models**: Salesforce/codegen-350M-mono, Salesforce/codegen-2B-mono
- **Small Models**: distilgpt2, gpt2, gpt2-medium
- **And many more...**

### **Gated Models (Require Hugging Face Token)**
- **LLaMA Models**: meta-llama/Llama-2-7b-chat-hf, meta-llama/Llama-2-13b-chat-hf
- **Mistral Models**: mistralai/Mistral-7B-Instruct-v0.2
- **Gemma Models**: google/gemma-2b, google/gemma-7b
- **CodeLlama Models**: codellama/CodeLlama-7b-hf

**Note**: For gated models, you need to:
1. Request access on the model's Hugging Face page
2. Get a token from https://huggingface.co/settings/tokens
3. Pass the token in the `hf_token` parameter

## Configuration

### Environment Variables

You can set the following environment variables:

- `CUDA_VISIBLE_DEVICES`: Specify which GPU to use
- `TRANSFORMERS_CACHE`: Set custom cache directory for models
- `HF_HOME`: Set Hugging Face home directory

### Authentication for Gated Models

For models that require authentication (like LLaMA, Gemma, etc.):

1. **Get a Hugging Face Token**:
   - Go to https://huggingface.co/settings/tokens
   - Create a new token with appropriate permissions

2. **Request Model Access**:
   - Visit the model page on Hugging Face (e.g., https://huggingface.co/google/gemma-2b)
   - Click "Request access" and follow the instructions

3. **Use the Token**:
   ```bash
   # Login via CLI
   huggingface-cli login
   
   # Or pass token in API request
   curl -X POST "http://localhost:8000/deploy" \
        -H "Content-Type: application/json" \
        -d '{
          "model_name": "google/gemma-2b",
          "hf_token": "your_token_here"
        }'
   ```

### CPU-Only Configuration

This service is optimized for CPU-only environments like VMs. Quantization options are disabled to ensure compatibility:

```json
{
  "model_name": "microsoft/DialoGPT-medium",
  "device": "cpu"
}
```

**Note**: For VM environments, it's recommended to use smaller models that can fit in available RAM.

## Performance Tips

1. **Choose Smaller Models**: For VM environments, use models under 1B parameters for optimal performance
2. **Monitor Memory Usage**: Ensure sufficient RAM for your chosen model
3. **Batch Processing**: The service supports single queries; for batch processing, consider extending the API
4. **Model Caching**: Models are cached locally after first download

## Troubleshooting

### Common Issues

1. **Out of Memory**: Use smaller models that fit in available RAM
2. **Model Loading Errors**: Check model name and ensure `trust_remote_code=True` for custom models
3. **Slow Performance**: Consider using smaller models for faster inference on CPU

### Logs

The service provides detailed logging. Check the console output for:
- Model loading progress
- Generation errors
- Memory usage information

## Development

### Project Structure

```
opensource_llm_deployment/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── .gitignore          # Git ignore file
```

### Adding Features

To extend the service:

1. **New Model Types**: Add support for different model architectures
2. **Batch Processing**: Implement batch query endpoints
3. **Model Management**: Add support for multiple concurrent models
4. **Authentication**: Add API key authentication
5. **Rate Limiting**: Implement request rate limiting

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
