#!/bin/bash
# Docker entrypoint for Intermap

set -e

echo "🗺️  Starting Intermap in Docker..."

# Start IPFS daemon in background
echo "Starting IPFS daemon..."
ipfs daemon --enable-pubsub-experiment &
IPFS_PID=$!

# Wait for IPFS to be ready
sleep 5

# Trap exit signals to cleanup
cleanup() {
    echo "Stopping IPFS daemon..."
    kill $IPFS_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGTERM SIGINT

# Execute main command
exec "$@"
