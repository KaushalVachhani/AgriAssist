# 🌾 AgriAssist

**Farm AI Assistant | खेत सहायक AI**

[![Production Ready](https://img.shields.io/badge/Production-Ready-green.svg)](https://github.com/agriassist/agriassist)
[![Security](https://img.shields.io/badge/Security-Enhanced-blue.svg)](https://github.com/agriassist/agriassist)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

AgriAssist is a production-ready, AI-powered farming assistant that provides expert agricultural advice through multimodal inputs. Built with modern security practices and a premium user interface, it helps farmers solve agricultural challenges using text, image, and audio queries.

## ✨ Features

### Core Functionality
- 🌱 **Multimodal Input**: Support for text, image, and audio queries
- 🗣️ **Multilingual**: Hindi language support with audio responses
- 🛡️ **Smart Guardrails**: LLM-based filtering for farming-related queries only
- 🎵 **Audio Responses**: Text-to-speech in Hindi for accessibility

### Production Features
- 🔒 **Security First**: Rate limiting, file validation, CORS protection
- 📱 **Premium UI**: Modern, responsive design with dark mode support
- ⚡ **Performance**: Production-ready Docker builds with smart path resolution
- 🔧 **Monitoring**: Health checks and comprehensive logging
- 📊 **Validation**: Input sanitization and file size limits

## 🏗️ Architecture

```
frontend/           # Modern HTML/CSS/JS interface
src/
  agriassist/      # Main application package
    config.py      # Configuration and settings
    handlers.py    # Request processing and validation
    ui.py          # FastAPI application with security
    __init__.py    # Package initialization
  app.py           # Application entry point
pyproject.toml     # Modern Python project configuration
Dockerfile         # Production-ready Docker build with path resolution
uv.lock           # Dependency lock file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- API keys for Groq and Google Gemini

### 1. Install Dependencies
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

### 2. Environment Setup
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Customize settings
APP_NAME="Farm AI Assistant"
DEBUG=false
LOG_LEVEL=INFO
MAX_FILE_SIZE=10485760  # 10MB
REQUESTS_PER_MINUTE=30
```

### 3. Run the Application
```bash
# Development
uv run python src/app.py

# Production with uvicorn
uv run uvicorn agriassist.ui:app --host 0.0.0.0 --port 7860
```

### 4. Access the Application
Open [http://localhost:7860](http://localhost:7860) in your browser

## 🐳 Docker Deployment

✅ **Production Ready!** AgriAssist is fully containerized with automatic path resolution and pip-based dependencies for maximum compatibility.

🔧 **Latest Updates:**
- ✅ Fixed frontend path resolution for Docker environments
- ✅ Automatic dev/production path detection
- ✅ Optimized for cross-platform deployment
- ✅ Comprehensive test script included

📖 **Detailed Guide**: See [README-DOCKER.md](./README-DOCKER.md) for comprehensive Docker deployment instructions.

### 🧪 Test Docker Setup
```bash
# Quick test with included script
chmod +x test-docker.sh
./test-docker.sh

# This will:
# - Build the image
# - Check environment setup  
# - Start container on port 7861
# - Verify health endpoint
```

### 🚀 Quick Production Start
```bash
# 1. Copy environment template and add your API keys
cp sample.env .env
# Edit .env with: GROQ_API_KEY=your_key, GOOGLE_API_KEY=your_key

# 2. Run with Docker Compose (Recommended)
docker-compose up -d

# 3. Access at http://localhost:7860
curl http://localhost:7860/health
```

### 🔧 Manual Docker Commands
```bash
# Build optimized production image
docker build -t agriassist:latest .

# Run with environment variables
docker run -d \
  --name agriassist \
  -p 7860:7860 \
  -e GROQ_API_KEY=your_groq_api_key \
  -e GOOGLE_API_KEY=your_google_api_key \
  -v agriassist_audio:/app/agriassist/generated_speech_responses \
  agriassist:latest
```

### 🐳 Docker Features
The included `docker-compose.yml` provides:
- ✅ **Smart Path Resolution** - Works in dev and production
- ✅ **Environment Management** - Secure API key handling
- ✅ **Persistent Storage** - Audio files preserved across restarts
- ✅ **Health Monitoring** - Built-in health checks
- ✅ **Auto-Restart** - Production-ready resilience
- ✅ **Security First** - Non-root user execution

```bash
# Copy environment file and add your API keys
cp sample.env .env

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

## 🔧 Configuration

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | Required | Groq API key for speech processing |
| `GOOGLE_API_KEY` | Required | Google Gemini API key |
| `APP_NAME` | "Farm AI Assistant" | Application name |
| `DEBUG` | false | Enable debug mode |
| `LOG_LEVEL` | INFO | Logging level |
| `MAX_FILE_SIZE` | 10485760 | Max file upload size (bytes) |
| `REQUESTS_PER_MINUTE` | 30 | Rate limit per IP |
| `ALLOWED_ORIGINS` | localhost URLs | CORS allowed origins |

### Security Settings
- File type validation for uploads
- File size limits (10MB default)
- Rate limiting (30 requests/minute per IP)
- CORS protection with configurable origins
- Input sanitization and validation
- Non-root Docker container execution

## 🧪 Development

### Setup Development Environment
```bash
# Install with development dependencies
uv sync --extra dev

# Run linting and formatting
uv run ruff check .
uv run black .

# Run tests (when available)
uv run pytest
```

### 🐳 Docker Development
Docker setup is fully production-ready with automatic path resolution:

```bash
# Quick test deployment
./test-docker.sh

# Development with hot reload
docker-compose up --build

# Production testing
docker build -t agriassist . && docker run -p 7860:7860 agriassist
```

**Note**: All Docker path resolution issues have been resolved. The application automatically detects whether it's running in Docker or development mode.

### API Endpoints
- `POST /api/query` - Submit farming queries
- `GET /health` - Health check endpoint
- `GET /` - Frontend application
- `GET /audio/{filename}` - Generated audio files

## 📱 User Interface

The frontend features a premium, modern design with:
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Dark Mode Support**: Automatic system preference detection
- **Accessibility**: ARIA labels, keyboard navigation, screen reader support
- **Progressive Enhancement**: Works with JavaScript disabled
- **Premium Animations**: Smooth transitions and micro-interactions

## 🛡️ Security Features

- **Rate Limiting**: Prevents abuse with configurable limits
- **File Validation**: Strict file type and size checking
- **Input Sanitization**: Prevents injection attacks
- **CORS Protection**: Configurable allowed origins
- **Security Headers**: Comprehensive security headers
- **Non-root Execution**: Docker containers run as non-root user with automatic path resolution

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Ensure all checks pass: `uv run ruff check . && uv run black .`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Guidelines
- Follow Python PEP 8 style guidelines
- Add comprehensive tests for new features
- Update documentation for API changes
- Ensure security best practices

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) for high-performance API
- Powered by [Google Gemini](https://ai.google.dev/) for intelligent responses
- Speech processing by [Groq](https://groq.com/) for fast transcription
- UI components inspired by modern design systems

---

**Made with ❤️ for farmers worldwide | दुनिया भर के किसानों के लिए ❤️ के साथ बनाया गया**