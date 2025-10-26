<!--
Intermap - Deployment Instructions
Copyright (c) 2025 Jay Wenden
Licensed under CC-BY-NC-SA 4.0
-->

# Intermap - Deployment Instructions

## Quick Deploy (Machine with Docker Already Installed)

### Option 1: Pre-built Image (Easiest!)
```bash
# Host networking (recommended for accurate topology)
docker run -d \
  --network host \
  --cap-add NET_ADMIN \
  --cap-add NET_RAW \
  --name intermap \
  yourusername/intermap:latest

# Or with port mapping (more isolated but less accurate)
docker run -d \
  -p 8000:8000 \
  -p 5000:5000 \
  -p 5001:5001 \
  --cap-add NET_ADMIN \
  --cap-add NET_RAW \
  --name intermap \
  yourusername/intermap:latest
```

**That's it!** Access at http://localhost:8000

**Why host networking?**
- Shows real network path, not container NAT
- Better IPFS peer discovery
- More accurate topology mapping
- Essential for traceroute to work correctly

### Option 2: With Docker Compose (Recommended)
Create a `docker-compose.yml`:
```yaml
version: '3.8'
services:
  intermap:
    image: yourusername/intermap:latest
    network_mode: host  # Uses host network for accurate topology
    volumes:
      - ipfs-data:/home/intermap/.ipfs
    cap_add:
      - NET_ADMIN
      - NET_RAW
    restart: unless-stopped

volumes:
  ipfs-data:
```

Then run:
```bash
docker-compose up -d
```

**Note:** Host networking works best on Linux. On Mac/Windows with Docker Desktop, use port mapping instead (see Option 1).

### Option 3: Build from Source
```bash
# Clone the repository
git clone https://github.com/yourusername/intermap.git
cd intermap

# Build and run
docker-compose up -d
```

## Access Points
- **Web UI**: http://localhost:8000
- **API**: http://localhost:5000
- **IPFS**: http://localhost:5001/webui

## Commands
```bash
# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart

# Rebuild after code changes
docker-compose up -d --build
```

## What Gets Built
The Docker image includes:
- Python 3.11 + all dependencies
- Kubo IPFS daemon
- React frontend (pre-built)
- All system tools (traceroute, ping, etc.)

**No additional setup needed** - everything runs in the container!

## System Requirements
- Docker installed
- 2GB RAM minimum
- 500MB disk space for image

## Ports Used
- 5000 - API server
- 8000 - Web UI
- 5001 - IPFS API
- 4001 - IPFS Swarm (P2P)

## Troubleshooting

### Container won't start
```bash
docker-compose logs
```

### Port already in use
Edit `docker-compose.yml` and change port mappings:
```yaml
ports:
  - "8001:8000"  # Use 8001 instead of 8000
```

### Reset everything
```bash
docker-compose down -v
docker-compose up -d
```
