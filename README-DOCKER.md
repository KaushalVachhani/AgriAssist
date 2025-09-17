# 🐳 Docker Deployment Guide

This guide explains how to run AgriAssist using Docker, making it easy to deploy anywhere.

## 🚀 Quick Start

### Prerequisites
- Docker installed on your system
- Docker Compose (optional but recommended)
- API keys for Groq and Google Generative AI

### 1. Clone and Setup
```bash
git clone <repository-url>
cd AgriAssist

# Copy environment file and add your API keys
cp sample.env .env
# Edit .env file with your actual API keys
```

### 2. Set Environment Variables
Edit the `.env` file and add your API keys:
```env
GROQ_API_KEY=your_actual_groq_api_key
GOOGLE_API_KEY=your_actual_google_api_key
```

### 3. Run with Docker Compose (Recommended)
```bash
docker-compose up -d
```

### 4. Access the Application
Open your browser and go to: http://localhost:7860

## 🔧 Manual Docker Commands

### Build the Image
```bash
docker build -t agriassist .
```

### Run the Container
```bash
docker run -d \
  --name agriassist-app \
  -p 7860:7860 \
  -e GROQ_API_KEY=your_groq_api_key \
  -e GOOGLE_API_KEY=your_google_api_key \
  -v agriassist_audio:/app/agriassist/generated_speech_responses \
  agriassist
```

## 📋 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | ✅ Yes | - | Groq API key for speech-to-text |
| `GOOGLE_API_KEY` | ✅ Yes | - | Google AI API key for LLM |
| `APP_NAME` | ❌ No | Farm AI Assistant | Application name |
| `DEBUG` | ❌ No | false | Enable debug mode |
| `LOG_LEVEL` | ❌ No | INFO | Logging level |
| `ALLOWED_ORIGINS` | ❌ No | localhost:7860 | CORS allowed origins |
| `MAX_FILE_SIZE` | ❌ No | 10485760 | Max file upload size (bytes) |
| `GEMINI_MODEL_NAME` | ❌ No | gemini-2.5-flash | Google AI model |
| `WHISPER_MODEL_NAME` | ❌ No | whisper-large-v3 | Groq speech model |
| `REQUESTS_PER_MINUTE` | ❌ No | 30 | Rate limiting |

## 🔍 Health Check

Check if the application is running:
```bash
curl http://localhost:7860/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "AgriAssist API is running",
  "version": "0.1.0"
}
```

## 📦 Container Management

### View Logs
```bash
docker-compose logs -f agriassist
# OR
docker logs -f agriassist-app
```

### Stop the Application
```bash
docker-compose down
# OR
docker stop agriassist-app
```

### Update the Application
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

## 🚀 Production Deployment

### Cloud Platforms

#### AWS ECS
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker build -t agriassist .
docker tag agriassist:latest <account>.dkr.ecr.us-east-1.amazonaws.com/agriassist:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/agriassist:latest
```

#### Google Cloud Run
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/agriassist
gcloud run deploy --image gcr.io/PROJECT-ID/agriassist --platform managed
```

#### Azure Container Instances
```bash
# Build and push to ACR
az acr build --registry myregistry --image agriassist .
az container create --resource-group myResourceGroup --name agriassist --image myregistry.azurecr.io/agriassist:latest
```

## 🛡️ Security Notes

- The container runs as a non-root user for security
- Only necessary ports are exposed
- Environment variables should be kept secure
- Use secrets management in production
- Regular security updates recommended

## 🔧 Troubleshooting

### Common Issues

1. **API Keys Missing**
   ```
   Error: Required environment variable GROQ_API_KEY is missing
   ```
   Solution: Ensure API keys are set in .env file

2. **Port Already in Use**
   ```
   Error: Port 7860 is already in use
   ```
   Solution: Change port mapping in docker-compose.yml or stop conflicting service

3. **Permission Denied**
   ```
   Error: Permission denied for audio files
   ```
   Solution: Check volume permissions and container user settings

### Debug Mode
Run with debug logging:
```bash
docker-compose -f docker-compose.yml up -d
docker-compose exec agriassist bash
```

## 📞 Support

If you encounter issues:
1. Check the logs: `docker-compose logs agriassist`
2. Verify environment variables are set correctly
3. Ensure API keys are valid and have proper permissions
4. Check firewall and network settings
