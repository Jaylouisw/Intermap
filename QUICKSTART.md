<!--
Intermap - Quick Start Guide
Copyright (c) 2025 Jay Wenden
Licensed under CC-BY-NC-SA 4.0
-->

# 🗺️ Intermap - Quick Start Guide

*Created by Jay Wenden*

## Run with Docker (Easiest)

### 1. Pull and run the image:
```bash
docker run -d \
  --network host \
  --cap-add NET_ADMIN \
  --cap-add NET_RAW \
  --name intermap \
  yourusername/intermap:latest
```

### 2. Access the interface:
- **Web UI**: http://localhost:8000
- **API**: http://localhost:5000
- **IPFS WebUI**: http://localhost:5001/webui

### 3. Check logs:
```bash
docker logs -f intermap
```

### 4. Stop:
```bash
docker stop intermap
docker rm intermap
```

---

## What is Intermap?

A **fully distributed P2P network topology mapper** where:
- Participants run Docker containers that perform traceroutes
- Each hop becomes a node, RTT becomes edge weight
- Data stored on IPFS (distributed, no central server)
- Creates collaborative internet infrastructure map
- Export to GEXF format for Gephi analysis

---

## Privacy & Security

✅ **Only public IPs shared** - RFC1918 private addresses automatically filtered  
✅ **Anonymous participation** - No identity data collected  
✅ **Distributed storage** - IPFS content addressing  
✅ **No central authority** - Pure P2P coordination via IPFS DHT

---

## Requirements

- **Docker** (that's it!)
- 2GB RAM minimum
- 500MB disk space

Install Docker: https://www.docker.com/products/docker-desktop/

---

## Alternative: Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  intermap:
    image: yourusername/intermap:latest
    network_mode: host
    cap_add:
      - NET_ADMIN
      - NET_RAW
    volumes:
      - ipfs-data:/home/intermap/.ipfs
    restart: unless-stopped

volumes:
  ipfs-data:
```

Then:
```bash
docker-compose up -d
```

---

## Configuration

Environment variables:
```bash
docker run -d \
  --network host \
  --cap-add NET_ADMIN \
  --cap-add NET_RAW \
  -e NODE_UPDATE_INTERVAL=300 \
  -e TARGET_SUBNET="8.8.8.0/28" \
  --name intermap \
  yourusername/intermap:latest
```

Or mount custom config:
```bash
docker run -d \
  --network host \
  -v ./config.yaml:/app/config/default.yaml \
  --name intermap \
  yourusername/intermap:latest
```

---

## Troubleshooting

### Docker not installed?
```bash
# Check
docker --version

# Install from https://www.docker.com/products/docker-desktop/
```

### Can't access Web UI?
- Check container is running: `docker ps`
- View logs: `docker logs intermap`
- Try: http://127.0.0.1:8000

### IPFS not connecting?
- IPFS daemon starts automatically in container
- Check: http://localhost:5001/webui
- May take 30-60s to find peers on first run
- View peers: `docker exec intermap ipfs swarm peers`

### Traceroute not working?
- Container needs NET_ADMIN and NET_RAW capabilities (already included)
- Some networks block ICMP/UDP
- Check logs for errors

### Port conflicts?
Use bridge networking instead:
```bash
docker run -d \
  -p 8001:8000 \
  -p 5001:5000 \
  --cap-add NET_ADMIN \
  --cap-add NET_RAW \
  --name intermap \
  yourusername/intermap:latest
```

---

## Architecture

### Container Includes:
- Python 3.11 runtime
- Kubo IPFS daemon
- React frontend (pre-built)
- Traceroute tools
- Bandwidth testing (iperf3)

### P2P Coordination:
1. Node announces via IPFS CID
2. Discovers peers through DHT
3. Publishes topology to IPFS
4. Pins content for availability
5. No central server needed!

---

## Advanced Usage

### View IPFS node info:
```bash
docker exec intermap ipfs id
```

### Export topology:
```bash
docker cp intermap:/app/output/topology_latest.gexf ./
```

### Custom traceroute targets:
Edit `config/default.yaml`:
```yaml
node:
  target_subnet: "1.1.1.0/28"  # Change this
```

### View in Gephi:
1. Download Gephi: https://gephi.org/
2. Open `topology_latest.gexf`
3. Apply Force Atlas 2 layout
4. Color edges by RTT weight

---

## License

**CC-BY-NC-SA 4.0** - Copyright (c) 2025 Jay Wenden

See [LICENSE](LICENSE) for details.

---

**Created by Jay Wenden** | [GitHub](https://github.com/YOUR_USERNAME/intermap)

### 1. Build the image:
```bash
python build.py
```

### 2. Start Intermap:
```bash
docker-compose up -d
```

### 3. Access the interface:
- **Web UI**: http://localhost:8000
- **API**: http://localhost:5000
- **IPFS WebUI**: http://localhost:5001/webui

### 4. Check logs:
```bash
docker-compose logs -f
```

### 5. Stop:
```bash
docker-compose down
```

---

## What is Intermap?

A **fully distributed P2P network topology mapper** where:
- Participants run nodes that perform traceroutes
- Each hop becomes a node, RTT becomes edge weight
- Data stored on IPFS (distributed, no central server)
- Creates collaborative internet infrastructure map
- Export to GEXF format for Gephi analysis

---

## Privacy & Security

✅ **Only public IPs shared** - RFC1918 private addresses automatically filtered  
✅ **Anonymous participation** - No identity data collected  
✅ **Distributed storage** - IPFS content addressing  
✅ **No central authority** - Pure P2P coordination

---

## Requirements

- **Docker** & **Docker Compose**
- That's it! Everything else is containerized

Install Docker: https://www.docker.com/products/docker-desktop/

---

## Manual Run (Without Docker)

If you want to run natively:

### 1. Install dependencies:
```bash
# Install Kubo IPFS daemon
# Download from: https://dist.ipfs.tech/#kubo

# Install Python requirements
pip install -r requirements.txt

# Build frontend
cd frontend
npm install
npm run build
cd ..
```

### 2. Start IPFS daemon:
```bash
ipfs daemon --enable-pubsub-experiment
```

### 3. Start Intermap:
```bash
python launch.py
```

---

## Configuration

Edit `config/default.yaml`:

```yaml
ipfs:
  api_url: "http://127.0.0.1:5001"
  gateway_url: "http://127.0.0.1:8080"

node:
  update_interval: 300  # seconds between updates
  scan_subnet: true
  target_subnet: "8.8.8.0/28"  # Example subnet to map

api:
  host: "0.0.0.0"
  port: 5000
```

---

## Advanced Usage

### Custom subnet scanning:
```bash
docker-compose run intermap python -m src.cli scan --subnet 1.1.1.0/28
```

### Export topology:
```bash
docker-compose run intermap python -m src.cli export
# Find GEXF in output/ folder
```

### View in Gephi:
1. Download Gephi: https://gephi.org/
2. Open `output/topology_latest.gexf`
3. Apply Force Atlas 2 layout
4. Color edges by RTT weight

---

## Troubleshooting

### Docker build fails:
```bash
# Clean rebuild
docker-compose down -v
docker system prune -a
python build.py
```

### Can't access Web UI:
- Check container is running: `docker-compose ps`
- View logs: `docker-compose logs -f`
- Try: http://127.0.0.1:8000

### IPFS not connecting:
- IPFS daemon starts automatically in container
- Check IPFS: http://localhost:5001/webui
- May take 30-60s to find peers on first run

### Traceroute not working:
- Container needs NET_ADMIN capability (already in docker-compose.yml)
- Some networks block ICMP/UDP

---

## Architecture

```
┌─────────────┐
│   Browser   │
│  localhost  │
│    :8000    │
└──────┬──────┘
       │
┌──────▼──────┐     ┌──────────┐
│   Docker    │────▶│   IPFS   │
│  Container  │     │  Network │
│             │     │  (P2P)   │
│  - Python   │     └──────────┘
│  - Node.js  │
│  - IPFS     │
│  - Frontend │
└─────────────┘
```

**Fully distributed** - No central server required!

---

## Contributing

See main repository for development guidelines.

---

## License

See `LICENSE` file.
