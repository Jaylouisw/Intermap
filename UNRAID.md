# Unraid Community Applications Guide

## About

Intermap is now available as an Unraid template! This guide explains how to install and use Intermap on Unraid systems.

## Installation

### Method 1: Community Applications (Recommended - After Approval)

Once approved in CA:

1. Open Unraid web interface
2. Go to **Apps** tab
3. Search for **"Intermap"**
4. Click **Install**
5. Configure settings (defaults work fine)
6. Click **Apply**

### Method 2: Manual Template Installation (Available Now)

1. Download `intermap.xml` from: https://raw.githubusercontent.com/Jaylouisw/Intermap/master/intermap.xml
2. In Unraid, go to **Docker** tab
3. Click **Add Container**
4. At the bottom, click **Template repositories**
5. Add: `https://github.com/Jaylouisw/Intermap`
6. Or manually paste the XML content

### Method 3: Docker Command

```bash
docker run -d \
  --name=intermap \
  --cap-add=NET_ADMIN \
  --cap-add=NET_RAW \
  -p 5000:5000 \
  -p 4001:4001 \
  -p 5201:5201 \
  -v /mnt/user/appdata/intermap/ipfs:/home/intermap/.ipfs \
  -v /mnt/user/appdata/intermap/output:/app/output \
  --restart unless-stopped \
  jaylouisw/intermap:latest
```

## Configuration

### Default Ports

- **5000**: Web UI and API
- **4001**: IPFS peer-to-peer
- **5201**: iperf3 bandwidth testing

### Storage Paths

- **IPFS Data**: `/mnt/user/appdata/intermap/ipfs` - Stores peer identity and IPFS blocks
- **Output**: `/mnt/user/appdata/intermap/output` - Topology GEXF files and node info

### Environment Variables

Available in advanced settings:

- `NODE_UPDATE_INTERVAL`: Seconds between updates (default: 300)
- `TARGET_SUBNET`: Specific subnet to map (e.g., "8.8.8.0/28")
- `LOG_LEVEL`: DEBUG, INFO, WARNING, or ERROR

## Usage

### Access the Web UI

After starting the container:

1. Open browser to: `http://[UNRAID-IP]:5000`
2. Wait 2-3 minutes for initial setup
3. Watch the network topology form!

### What You'll See

- **Nodes**: Network hops (routers, hosts)
- **Edges**: Connections colored by bandwidth
  - 🔵 Cyan: 10+ Gbps
  - 🟢 Green: 1-10 Gbps
  - 🟡 Yellow: 100 Mbps - 1 Gbps
  - 🟠 Orange: 10-100 Mbps
  - 🔴 Red: <10 Mbps

### View Logs

In Unraid Docker tab:
1. Click **Intermap** container
2. Click **Logs**

Or via console:
```bash
docker logs -f intermap
```

### Export Topology Data

Topology files are saved to `/mnt/user/appdata/intermap/output/`:
- `topology_latest.gexf` - Current network map
- `topology_YYYYMMDD_HHMMSS.gexf` - Historical snapshots

Open GEXF files in Gephi for advanced analysis.

## Privacy & Security

✅ **Only public IPs shared** - Private addresses (192.168.x.x, 10.x.x.x, 172.16-31.x.x) automatically filtered  
✅ **Anonymous participation** - No personal data collected  
✅ **Distributed storage** - Uses IPFS, no central server  
✅ **Open source** - Auditable code on GitHub

## Troubleshooting

### Container Won't Start

Check logs for errors:
```bash
docker logs intermap
```

Common issues:
- Port conflicts: Change port mappings if 5000/4001/5201 already in use
- Permissions: Ensure appdata directory is writable

### Can't Access Web UI

- Verify container is running: Docker tab should show "Started"
- Check Unraid firewall settings
- Try: `http://[UNRAID-IP]:5000` instead of `localhost`

### No Network Topology Showing

- Wait 2-3 minutes for initial subnet scan
- Check your network has live hosts
- View logs to see traceroute activity

### IPFS Not Connecting

- IPFS takes 30-60 seconds to find peers on first run
- Check port 4001 is not blocked by router/firewall
- View IPFS peers: `docker exec intermap ipfs swarm peers`

### High CPU Usage

Normal during initial subnet scan (2-3 minutes). Should stabilize after.

## Submitting to Community Applications

To submit Intermap to Unraid CA:

1. Fork: https://github.com/Unraid-CA/docker-templates
2. Add `intermap.xml` to the repository
3. Submit pull request with description
4. Wait for CA moderator approval

Template URL: `https://raw.githubusercontent.com/Jaylouisw/Intermap/master/intermap.xml`

## Updates

Unraid auto-updates are supported. To manually update:

1. Docker tab → Click **Intermap**
2. Click **Force Update**
3. Container will pull latest image and restart

## Support

- **GitHub Issues**: https://github.com/Jaylouisw/Intermap/issues
- **Documentation**: https://github.com/Jaylouisw/Intermap
- **Docker Hub**: https://hub.docker.com/r/jaylouisw/intermap

## Contributing

Help improve Intermap! See [CONTRIBUTING.md](https://github.com/Jaylouisw/Intermap/blob/master/CONTRIBUTING.md)

---

**Created by Jay Wenden** | Licensed under CC-BY-NC-SA 4.0
