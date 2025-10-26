#!/bin/bash
# Docker entrypoint for Intermap

set -e

echo "🗺️  Starting Intermap in Docker..."

# Start iperf3 server in background
echo "Starting iperf3 server on port 5201..."
iperf3 -s -D

# Start IPFS daemon in background
echo "Starting IPFS daemon..."
ipfs daemon --enable-pubsub-experiment &
IPFS_PID=$!

# Wait for IPFS to be ready
sleep 5

# Start simple HTTP server for frontend in background
echo "Starting web interface on port 8000..."
cd /app/frontend/build
python3 -m http.server 8000 &
WEB_PID=$!

cd /app

# Trap exit signals to cleanup
cleanup() {
    echo "Stopping services..."
    kill $IPFS_PID 2>/dev/null || true
    kill $WEB_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGTERM SIGINT

# Execute main command
exec "$@"
