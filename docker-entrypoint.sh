#!/bin/bash
# Docker entrypoint for Intermap

set -e

echo "🗺️  Starting Intermap in Docker..."

# Ensure output directory has correct permissions (already created in Dockerfile)
chmod 777 /app/output 2>/dev/null || true

# Start iperf3 server in background
echo "Starting iperf3 server on port 5201..."
iperf3 -s -D

# Start IPFS daemon in background
echo "Starting IPFS daemon..."
ipfs daemon --enable-pubsub-experiment &
IPFS_PID=$!

# Wait for IPFS to be ready
sleep 5

cd /app

# Start API server (which also serves the frontend)
# Uses PORT env var if set (Railway/Heroku), otherwise defaults to 5000
echo "Starting API server (serves both API and frontend)..."
python3 -m src.api_server &
API_PID=$!

# Trap exit signals to cleanup
cleanup() {
    echo "Stopping services..."
    kill $IPFS_PID 2>/dev/null || true
    kill $API_PID 2>/dev/null || true
    kill $MAIN_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGTERM SIGINT

# Start main application in background
"$@" &
MAIN_PID=$!

# Wait for main process
wait $MAIN_PID
