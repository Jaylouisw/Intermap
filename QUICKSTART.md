# 🗺️ Intermap - Quick Start Guide

## Run with Docker (Easiest)

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
