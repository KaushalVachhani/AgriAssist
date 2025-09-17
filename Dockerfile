# Production-ready Dockerfile for AgriAssist
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for security
RUN groupadd -r agriassist && useradd -r -g agriassist agriassist

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./
COPY frontend/ ./frontend/

# Create necessary directories
RUN mkdir -p /app/agriassist/generated_speech_responses && \
    chown -R agriassist:agriassist /app

# Set proper permissions
RUN chmod -R 755 /app && \
    chmod -R 777 /app/agriassist/generated_speech_responses && \
    chmod -R 755 /app/frontend

# Switch to non-root user
USER agriassist

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Expose port
EXPOSE 7860

# Start the application
CMD ["python", "app.py"]