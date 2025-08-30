# Docker Deployment Guide for Ubuntu Server

This guide will help you deploy the LLM Deployment Service on an Ubuntu server using Docker.

## 🚀 Quick Start

### 1. Prerequisites

Ensure your Ubuntu server has:
- Ubuntu 18.04 or later
- At least 4GB RAM (8GB recommended)
- At least 10GB free disk space
- Internet connection

### 2. Install Docker and Docker Compose

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install docker.io docker-compose -y

# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (optional)
sudo usermod -aG docker $USER
# Log out and back in for this to take effect
```

### 3. Transfer Project Files

**Option A: Using Git (Recommended)**
```bash
# Clone the repository
git clone <your-repo-url>
cd opensource_llm_deployment
```

**Option B: Using SCP**
```bash
# From your local machine
scp -r /path/to/your/opensource_llm_deployment user@your-server-ip:/home/user/
```

### 4. Deploy the Service

```bash
# Navigate to project directory
cd opensource_llm_deployment

# Make scripts executable
chmod +x deploy.sh manage.sh

# Run full deployment
./deploy.sh
```

## 📋 Docker Commands Reference

### Basic Docker Commands

```bash
# Build the image
docker build -t llm-deployment-service .

# Run the container
docker run -d \
  --name llm-service \
  -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  -v model-cache:/app/.cache \
  --restart unless-stopped \
  llm-deployment-service

# Check running containers
docker ps

# View logs
docker logs llm-service

# Stop container
docker stop llm-service

# Remove container
docker rm llm-service
```

### Docker Compose Commands

```bash
# Start service
docker-compose up -d

# Stop service
docker-compose down

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Restart service
docker-compose restart

# Build image
docker-compose build --no-cache
```

### Management Script Commands

```bash
# Full deployment
./manage.sh deploy

# Start service
./manage.sh start

# Stop service
./manage.sh stop

# Restart service
./manage.sh restart

# View logs
./manage.sh logs

# Check status
./manage.sh status

# Test API
./manage.sh test

# Clean up
./manage.sh clean
```

## 🔧 Configuration

### Environment Variables

You can customize the deployment by setting environment variables:

```bash
# Create .env file
cat > .env << EOF
TRANSFORMERS_CACHE=/app/.cache/transformers
HF_HOME=/app/.cache/huggingface
EOF
```

### Port Configuration

To change the port, modify `docker-compose.yml`:

```yaml
ports:
  - "8080:8000"  # Change 8080 to your desired port
```

### Volume Configuration

The service uses volumes for:
- Model cache: `model-cache:/app/.cache`
- Logs: `./logs:/app/logs`

## 🧪 Testing the Deployment

### 1. Test API Health

```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "service": "Open Source LLM Deployment Service",
  "version": "1.0.0",
  "endpoints": {
    "deploy": "POST /deploy - Deploy a model from Hugging Face",
    "query": "POST /query - Query the deployed model",
    "status": "GET /status - Get model status",
    "undeploy": "DELETE /undeploy - Undeploy current model"
  }
}
```

### 2. Deploy a Model

```bash
curl -X POST "http://localhost:8000/deploy" \
     -H "Content-Type: application/json" \
     -d '{
       "model_name": "microsoft/DialoGPT-medium",
       "device": "cpu"
     }'
```

### 3. Query the Model

```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "Hello, how are you?",
       "max_length": 50
     }'
```

## 📊 Monitoring

### View Logs

```bash
# Real-time logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100
```

### Check Resource Usage

```bash
# Container resource usage
docker stats llm-service

# Disk usage
docker system df
```

### Health Check

The service includes a health check endpoint:

```bash
curl http://localhost:8000/status
```

## 🔒 Security Considerations

### 1. Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 8000/tcp  # API port
sudo ufw allow 22/tcp    # SSH (if needed)
sudo ufw enable
```

### 2. Reverse Proxy (Optional)

For production, consider using Nginx as a reverse proxy:

```bash
# Install Nginx
sudo apt install nginx

# Configure Nginx (create /etc/nginx/sites-available/llm-service)
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using port 8000
   sudo netstat -tulpn | grep :8000
   
   # Kill the process or change port
   ```

2. **Out of Memory**
   ```bash
   # Check memory usage
   free -h
   
   # Use smaller models or increase server RAM
   ```

3. **Docker Permission Issues**
   ```bash
   # Add user to docker group
   sudo usermod -aG docker $USER
   
   # Log out and back in
   ```

4. **Container Won't Start**
   ```bash
   # Check logs
   docker-compose logs
   
   # Check if port is available
   sudo lsof -i :8000
   ```

### Debug Commands

```bash
# Check Docker daemon status
sudo systemctl status docker

# Check container details
docker inspect llm-service

# Check image details
docker images llm-deployment-service

# Check volume details
docker volume ls
```

## 📈 Performance Optimization

### 1. Resource Limits

Add resource limits to `docker-compose.yml`:

```yaml
services:
  llm-service:
    # ... existing config ...
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'
```

### 2. Model Caching

Models are automatically cached in the `model-cache` volume. To persist across deployments:

```bash
# Backup model cache
docker run --rm -v model-cache:/cache -v $(pwd):/backup alpine tar czf /backup/model-cache.tar.gz -C /cache .

# Restore model cache
docker run --rm -v model-cache:/cache -v $(pwd):/backup alpine tar xzf /backup/model-cache.tar.gz -C /cache
```

## 🎯 Production Checklist

- [ ] Docker and Docker Compose installed
- [ ] Service deployed and running
- [ ] API responding correctly
- [ ] Model deployment working
- [ ] Logs being generated
- [ ] Resource monitoring configured
- [ ] Backup strategy in place
- [ ] Security measures implemented
- [ ] Documentation updated

## 📞 Support

If you encounter issues:

1. Check the logs: `./manage.sh logs`
2. Verify system resources: `free -h && df -h`
3. Test API connectivity: `./manage.sh test`
4. Review this documentation
5. Check the troubleshooting section in `TROUBLESHOOTING.md`
