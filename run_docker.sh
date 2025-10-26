#!/bin/bash
# Quick start script for running Intermap in Docker
# This ensures proper port mappings and capabilities

echo "🗺️  Starting Intermap Docker Container..."

# Stop and remove existing container if running
if docker ps -a --filter "name=intermap" --format "{{.Names}}" | grep -q "^intermap$"; then
    echo "Stopping existing container..."
    docker stop intermap > /dev/null 2>&1
    docker rm intermap > /dev/null 2>&1
fi

# Pull latest image
echo "Pulling latest image from Docker Hub..."
docker pull jaylouisw/intermap:latest

# Run container with proper configuration
echo "Starting container with port mappings..."
docker run -d \
    --name intermap \
    --cap-add=NET_ADMIN \
    --cap-add=NET_RAW \
    -p 5000:5000 \
    -p 4001:4001 \
    -p 5201:5201 \
    -v intermap-ipfs:/home/intermap/.ipfs \
    -v intermap-output:/app/output \
    jaylouisw/intermap:latest

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Intermap is starting!"
    echo ""
    echo "📊 Web UI: http://localhost:5000"
    echo "🔌 IPFS:   Port 4001"
    echo "📡 iperf3: Port 5201"
    echo ""
    echo "📋 View logs:   docker logs -f intermap"
    echo "⏹️  Stop:        docker stop intermap"
    echo ""
    echo "⏳ Give it 10-15 seconds to start, then open http://localhost:5000"
else
    echo ""
    echo "❌ Failed to start container!"
    echo "Check Docker is running: docker ps"
    exit 1
fi
