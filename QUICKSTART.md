# ⚡ Quick Start Guide<!--

Intermap - Quick Start Guide

Get Intermap running in 60 seconds!Copyright (c) 2025 Jay Wenden

Licensed under CC-BY-NC-SA 4.0

----->



## 🐳 Docker (Easiest - Recommended)# 🗺️ Intermap - Quick Start Guide



### Prerequisites*Created by Jay Wenden*



- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))## Run with Docker (Easiest)

- That's it!

### 1. Pull and run the image:

### One Command to Rule Them All```bash

docker run -d \

**Linux:**  --network host \

```bash  --cap-add NET_ADMIN \

docker run -d \  --cap-add NET_RAW \

  --name intermap \  --name intermap \

  --network host \  yourusername/intermap:latest

  --cap-add NET_ADMIN \```

  --cap-add NET_RAW \

  --restart unless-stopped \### 2. Access the interface:

  YOUR_USERNAME/intermap:latest- **Web UI**: http://localhost:8000

```- **API**: http://localhost:5000

- **IPFS WebUI**: http://localhost:5001/webui

**Windows/Mac (use bridge networking):**

```bash### 3. Check logs:

docker run -d \```bash

  --name intermap \docker logs -f intermap

  -p 8000:8000 \```

  -p 4001:4001 \

  -p 5201:5201 \### 4. Stop:

  --cap-add NET_ADMIN \```bash

  --cap-add NET_RAW \docker stop intermap

  --restart unless-stopped \docker rm intermap

  YOUR_USERNAME/intermap:latest```

```

---

### Access the UI

## What is Intermap?

Open your browser: **http://localhost:8000**

A **fully distributed P2P network topology mapper** where:

That's it! You're now mapping the internet! 🌐- Participants run Docker containers that perform traceroutes

- Each hop becomes a node, RTT becomes edge weight

---- Data stored on IPFS (distributed, no central server)

- Creates collaborative internet infrastructure map

## 🐙 Docker Compose- Export to GEXF format for Gephi analysis



```bash---

git clone https://github.com/YOUR_USERNAME/intermap.git

cd intermap## Privacy & Security

docker-compose up -d

```✅ **Only public IPs shared** - RFC1918 private addresses automatically filtered  

✅ **Anonymous participation** - No identity data collected  

Open: **http://localhost:8000**✅ **Distributed storage** - IPFS content addressing  

✅ **No central authority** - Pure P2P coordination via IPFS DHT

---

---

## 💻 From Source (Development)

## Requirements

### Prerequisites

- **Docker** (that's it!)

- Python 3.9+- 2GB RAM minimum

- Node.js 16+- 500MB disk space

- IPFS daemon ([Install IPFS](https://docs.ipfs.io/install/))

Install Docker: https://www.docker.com/products/docker-desktop/

### Setup

---

```bash

# Clone repository## Alternative: Docker Compose

git clone https://github.com/YOUR_USERNAME/intermap.git

cd intermapCreate `docker-compose.yml`:

```yaml

# Create virtual environmentversion: '3.8'

python -m venv .venvservices:

  intermap:

# Activate (Windows)    image: yourusername/intermap:latest

.venv\Scripts\activate    network_mode: host

# Activate (Linux/Mac)    cap_add:

source .venv/bin/activate      - NET_ADMIN

      - NET_RAW

# Install Python dependencies    volumes:

pip install -r requirements.txt      - ipfs-data:/home/intermap/.ipfs

    restart: unless-stopped

# Build frontend

cd frontendvolumes:

npm install  ipfs-data:

npm run build```

cd ..

Then:

# Start IPFS (separate terminal)```bash

ipfs daemondocker-compose up -d

```

# Run Intermap

python src/main.py---

```

## Configuration

Open: **http://localhost:8000**

Environment variables:

---```bash

docker run -d \

## 🎮 What You'll See  --network host \

  --cap-add NET_ADMIN \

### Initial Startup (First 2-3 minutes)  --cap-add NET_RAW \

  -e NODE_UPDATE_INTERVAL=300 \

1. **IPFS Initialization**: Node connects to IPFS network  -e TARGET_SUBNET="8.8.8.0/28" \

2. **Subnet Detection**: Automatically finds your /24 subnet  --name intermap \

3. **Ping Sweep**: Discovers live hosts (parallel, very fast!)  yourusername/intermap:latest

4. **Traceroutes Begin**: Maps paths to:```

   - Live subnet hosts

   - Well-known targets (8.8.8.8, 1.1.1.1, etc.)Or mount custom config:

   - Other Intermap nodes (once discovered)```bash

docker run -d \

### Web Interface  --network host \

  -v ./config.yaml:/app/config/default.yaml \

- **Nodes**: Circles representing routers/hosts  --name intermap \

- **Edges**: Connections showing network paths  yourusername/intermap:latest

  - **Length**: Based on latency (shorter = faster)```

  - **Color**: Based on bandwidth

    - 🔵 Cyan/Blue: Multi-gigabit (10+ Gbps)---

    - 🟢 Green: Gigabit+ (1-10 Gbps)

    - 🟡 Yellow: Fast (100 Mbps - 1 Gbps)## Troubleshooting

    - 🟠 Orange: Medium (10-100 Mbps)

    - 🔴 Red: Slow (<10 Mbps)### Docker not installed?

```bash

### Click Any Node# Check

docker --version

- See IP address and hostname

- View latency measurements# Install from https://www.docker.com/products/docker-desktop/

- Check bandwidth (if tested)```

- See connected neighbors

### Can't access Web UI?

---- Check container is running: `docker ps`

- View logs: `docker logs intermap`

## 🔧 Basic Commands- Try: http://127.0.0.1:8000



### View Logs### IPFS not connecting?

- IPFS daemon starts automatically in container

```bash- Check: http://localhost:5001/webui

docker logs -f intermap- May take 30-60s to find peers on first run

```- View peers: `docker exec intermap ipfs swarm peers`



### Check IPFS Status### Traceroute not working?

- Container needs NET_ADMIN and NET_RAW capabilities (already included)

```bash- Some networks block ICMP/UDP

docker exec intermap ipfs id- Check logs for errors

docker exec intermap ipfs swarm peers

```### Port conflicts?

Use bridge networking instead:

### Run Specific Traceroute```bash

docker run -d \

```bash  -p 8001:8000 \

docker exec intermap python -m src.cli traceroute 1.1.1.1  -p 5001:5000 \

```  --cap-add NET_ADMIN \

  --cap-add NET_RAW \

### Test Bandwidth  --name intermap \

  yourusername/intermap:latest

```bash```

docker exec intermap python -m src.cli bandwidth 8.8.8.8

```---



### Export Map## Architecture



```bash### Container Includes:

docker exec intermap python -m src.cli export --format gexf- Python 3.11 runtime

```- Kubo IPFS daemon

- React frontend (pre-built)

---- Traceroute tools

- Bandwidth testing (iperf3)

## 🛑 Stop/Remove

### P2P Coordination:

```bash1. Node announces via IPFS CID

# Stop container2. Discovers peers through DHT

docker stop intermap3. Publishes topology to IPFS

4. Pins content for availability

# Remove container5. No central server needed!

docker rm intermap

---

# Remove data volume (careful!)

docker volume rm intermap_data## Advanced Usage

```

### View IPFS node info:

---```bash

docker exec intermap ipfs id

## ⚙️ Configuration```



### Environment Variables### Export topology:

```bash

Edit before running:docker cp intermap:/app/output/topology_latest.gexf ./

```

```bash

docker run -d \### Custom traceroute targets:

  -e TRACEROUTE_INTERVAL=300 \Edit `config/default.yaml`:

  -e BANDWIDTH_TEST_INTERVAL=3600 \```yaml

  -e LOG_LEVEL=INFO \node:

  ...  target_subnet: "1.1.1.0/28"  # Change this

``````



### Config File### View in Gephi:

1. Download Gephi: https://gephi.org/

Mount custom config:2. Open `topology_latest.gexf`

3. Apply Force Atlas 2 layout

```bash4. Color edges by RTT weight

docker run -d \

  -v $(pwd)/my-config.yaml:/app/config/default.yaml \---

  ...

```## License



Example `my-config.yaml`:**CC-BY-NC-SA 4.0** - Copyright (c) 2025 Jay Wenden



```yamlSee [LICENSE](LICENSE) for details.

traceroute:

  interval: 300---

  verify_reachable: true

  **Created by Jay Wenden** | [GitHub](https://github.com/YOUR_USERNAME/intermap)

bandwidth:

  enabled: true### 1. Build the image:

  interval: 3600```bash

  sequential_only: truepython build.py

  ```

well_known_targets:

  - 8.8.8.8### 2. Start Intermap:

  - 1.1.1.1```bash

  - 9.9.9.9docker-compose up -d

``````



---### 3. Access the interface:

- **Web UI**: http://localhost:8000

## ❓ Troubleshooting- **API**: http://localhost:5000

- **IPFS WebUI**: http://localhost:5001/webui

### Container Won't Start

### 4. Check logs:

```bash```bash

# Check logsdocker-compose logs -f

docker logs intermap```



# Verify Docker version### 5. Stop:

docker --version  # Should be 20.10+```bash

```docker-compose down

```

### Can't Access Web UI

---

- Check if port 8000 is available: `netstat -an | findstr 8000` (Windows) or `lsof -i :8000` (Mac/Linux)

- Try different port: `-p 8001:8000`## What is Intermap?

- Check firewall settings

A **fully distributed P2P network topology mapper** where:

### Traceroute Not Working- Participants run nodes that perform traceroutes

- Each hop becomes a node, RTT becomes edge weight

- Ensure `--cap-add NET_ADMIN --cap-add NET_RAW` flags are included- Data stored on IPFS (distributed, no central server)

- On Windows/Mac, some network operations may be limited by Docker Desktop- Creates collaborative internet infrastructure map

- Export to GEXF format for Gephi analysis

### No Peers Found

---

- Wait 2-3 minutes for IPFS to connect

- Check IPFS status: `docker exec intermap ipfs swarm peers`## Privacy & Security

- Ensure port 4001 is not blocked by firewall

✅ **Only public IPs shared** - RFC1918 private addresses automatically filtered  

### High CPU Usage✅ **Anonymous participation** - No identity data collected  

✅ **Distributed storage** - IPFS content addressing  

Normal during initial subnet scan (2-3 minutes). Should stabilize after that.✅ **No central authority** - Pure P2P coordination



------



## 📚 Next Steps## Requirements



- **[Full README](README.md)**: Learn about all features- **Docker** & **Docker Compose**

- **[Contributing](CONTRIBUTING.md)**: Help improve Intermap- That's it! Everything else is containerized

- **[Deployment](DEPLOY.md)**: Deploy to cloud platforms

- **[Testing](TESTING.md)**: Run tests and CIInstall Docker: https://www.docker.com/products/docker-desktop/



------



## 🆘 Need Help?## Manual Run (Without Docker)



- **GitHub Issues**: [Report problems](https://github.com/YOUR_USERNAME/intermap/issues)If you want to run natively:

- **Discussions**: [Ask questions](https://github.com/YOUR_USERNAME/intermap/discussions)

- **Wiki**: [Check FAQ](https://github.com/YOUR_USERNAME/intermap/wiki)### 1. Install dependencies:

```bash

---# Install Kubo IPFS daemon

# Download from: https://dist.ipfs.tech/#kubo

**Happy mapping!** 🌐 You're now contributing to the global internet topology map!

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
