#!/bin/bash
# Test script for AgriAssist Docker deployment

echo "🐳 Testing AgriAssist Docker Setup"
echo "================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Clean up any existing test containers
echo "🧹 Cleaning up existing test containers..."
docker stop agriassist-test 2>/dev/null || true
docker rm agriassist-test 2>/dev/null || true

# Build the image
echo "🔨 Building Docker image..."
if docker build -t agriassist-test .; then
    print_status "Docker image built successfully"
else
    print_error "Docker build failed"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from sample..."
    cp sample.env .env
    echo ""
    echo "📝 Please edit .env file with your actual API keys:"
    echo "   GROQ_API_KEY=your_groq_api_key"
    echo "   GOOGLE_API_KEY=your_google_api_key"
    echo ""
    echo "Then run this script again or use: docker-compose up -d"
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

# Check if API keys are set
if [ -z "$GROQ_API_KEY" ] || [ "$GROQ_API_KEY" = "your_groq_api_key_here" ]; then
    print_error "GROQ_API_KEY not set in .env file"
    exit 1
fi

if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your_google_api_key_here" ]; then
    print_error "GOOGLE_API_KEY not set in .env file"
    exit 1
fi

# Run the container
echo "🚀 Starting AgriAssist container..."
docker run -d \
    --name agriassist-test \
    -p 7861:7860 \
    -e GROQ_API_KEY="$GROQ_API_KEY" \
    -e GOOGLE_API_KEY="$GOOGLE_API_KEY" \
    -e LOG_LEVEL=INFO \
    agriassist-test

if [ $? -eq 0 ]; then
    print_status "Container started successfully"
else
    print_error "Failed to start container"
    exit 1
fi

# Wait for the application to start
echo "⏳ Waiting for application to start..."
sleep 10

# Test health endpoint
echo "🔍 Testing health endpoint..."
if curl -s http://localhost:7861/health > /dev/null; then
    print_status "Health endpoint is responding"
    
    # Show health status
    echo "📊 Health Status:"
    curl -s http://localhost:7861/health | python3 -m json.tool
else
    print_error "Health endpoint is not responding"
    echo ""
    echo "📋 Container logs:"
    docker logs agriassist-test
    
    # Clean up
    docker stop agriassist-test
    docker rm agriassist-test
    exit 1
fi

echo ""
print_status "🎉 Docker test completed successfully!"
echo ""
echo "🌐 Access AgriAssist at: http://localhost:7861"
echo "🏥 Health check at: http://localhost:7861/health"
echo ""
echo "🛠️  Useful commands:"
echo "   View logs: docker logs -f agriassist-test"
echo "   Stop container: docker stop agriassist-test"
echo "   Remove container: docker rm agriassist-test"
echo ""
echo "🚀 For production deployment, use: docker-compose up -d"

