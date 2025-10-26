# 🌐 Intermap - Distributed Internet Topology Mapper

**Map the Internet, Together.**

[![Docker Build](https://github.com/jaylouisw/intermap/actions/workflows/docker-build.yml/badge.svg)](https://github.com/jaylouisw/intermap/actions/workflows/docker-build.yml)
[![Docker Hub](https://img.shields.io/docker/pulls/jaylouisw/intermap)](https://hub.docker.com/r/jaylouisw/intermap)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

*A distributed computing project that creates a collaborative, real-time map of global internet infrastructure through anonymous peer-to-peer participation.*

---

## 🎯 What is Intermap?

Intermap is a **fully decentralized network mapping system** where participants run nodes that collaboratively discover and visualize internet infrastructure. Every participant contributes to a shared, ever-growing map showing how data flows across the internet.

**Think of it as a crowdsourced, real-time "Google Maps" for internet routing paths.**

### 🔥 Why This Matters

- **🔍 Transparency**: See how your data actually travels across the internet
- **📊 Network Analysis**: Identify bottlenecks, routing inefficiencies, and network topology
- **🌍 Global Coverage**: More participants = more comprehensive mapping
- **🔒 Privacy-Focused**: Zero personal data collection, anonymous participation
- **🆓 100% Free & Open Source**: No subscriptions, no paywalls, no tracking

---

## ✨ Key Features

### 🚀 Intelligent Network Discovery

- **Smart Subnet Scanning**: Automatically detects and maps your public subnet with parallel ping sweeps (50 concurrent workers)
- **Live Host Detection**: Only maps responsive IPs - no time wasted on dead hosts
- **Comprehensive Traceroutes**: Every hop recorded with millisecond-precision RTT measurements
- **Well-Known Targets**: Pre-configured to map to DNS servers, root nameservers, and major CDNs

### ⚡ Multi-Gigabit Bandwidth Testing

- **iperf3 Integration**: Built-in bandwidth testing to measure actual throughput
- **Sequential Testing**: Accurate measurements without network congestion
- **Peak Tracking**: Keeps maximum detected bandwidth for optimal visualization
- **Modern Speed Support**: Color-coded up to **100 Gbps** datacenter speeds
  - 🔵 **Cyan**: 100+ Gbps (datacenter backbone)
  - 🔵 **Blue**: 10-40 Gbps (high-speed datacenter)
  - 🟢 **Green**: 2.5-10 Gbps (multi-gigabit fiber)
  - 🟡 **Yellow**: 100 Mbps - 1 Gbps (fast broadband)
  - 🟠 **Orange**: 10-100 Mbps (medium speed)
  - 🔴 **Red**: <10 Mbps (slow connections)

### 🤝 Collaborative Verification

- **Continuous Health Checks**: Pings all mapped IPs every 5 minutes
- **Cross-Node Verification**: Nodes confirm each other's findings for accuracy
- **Dead IP Removal**: Consensus-based cleanup of unreachable hosts
- **Multi-Perspective Routing**: See how different locations route to the same destination

### 🌐 Pure Peer-to-Peer Architecture

- **No Central Server**: 100% distributed coordination via IPFS
- **Censorship-Resistant**: Data stored on IPFS content-addressed network
- **Auto-Discovery**: Nodes find each other automatically through DHT
- **Resilient**: Network continues operating even if nodes go offline

### 🔐 Privacy by Design

- **Anonymous Participation**: No signup, no accounts, no identity tracking
- **RFC1918 Filtering**: Private IPs (10.x, 172.16-31.x, 192.168.x) NEVER shared
- **Public IPs Only**: Only internet-routable addresses included in maps
- **Transparent Code**: Fully open source - verify privacy yourself

### 📈 Powerful Visualization

- **Real-Time Web Interface**: Interactive network graph with vis.js
- **Bandwidth Legends**: Color-coded edges show connection speeds at a glance
- **Gephi Export**: GEXF format for advanced offline analysis
- **Node Inspection**: Click any hop to see latency, bandwidth, and routing details

---

## 🚀 Quick Start (60 Seconds)

**Just run this one command:**

```bash
# Linux (recommended - best accuracy)
docker run -d \
  --name intermap \
  --network host \
  --cap-add NET_ADMIN \
  --cap-add NET_RAW \
  jaylouisw/intermap:latest

# Windows/Mac (use bridge networking)
docker run -d \
  --name intermap \
  -p 8000:8000 \
  -p 4001:4001 \
  -p 5201:5201 \
  --cap-add NET_ADMIN \
  --cap-add NET_RAW \
  jaylouisw/intermap:latest
```

**That's it!** Open **http://localhost:8000** in your browser.

### 🛑 Stop/Remove

```bash
docker stop intermap
docker rm intermap
```

### 🔧 Advanced: Build from Source

Only for developers who want to modify code:

```bash
git clone https://github.com/jaylouisw/intermap.git
cd intermap
docker-compose up -d
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full development setup.

---

## 🎮 Usage

Once running, open **http://localhost:8000** in your browser.

### What You'll See

- **Nodes**: Circles representing routers/servers/hops
- **Edges**: Connections between hops
  - **Length**: Shorter = lower latency
  - **Color**: Bandwidth speed (cyan = fastest, red = slowest)
- **Your Subnet**: All live hosts automatically discovered and mapped
- **Peer Routes**: Paths to other Intermap participants
- **Well-Known Hosts**: Routes to 8.8.8.8, 1.1.1.1, root nameservers, etc.

### Bandwidth Color Legend

| Color | Speed | Typical Use |
|-------|-------|-------------|
| 🔵 Cyan/Blue | 10-100+ Gbps | Datacenter backbone |
| 🟢 Green | 1-10 Gbps | Multi-gigabit fiber |
| 🟡 Yellow | 100 Mbps - 1 Gbps | Fast broadband/gigabit |
| 🟠 Orange | 10-100 Mbps | Medium speed |
| 🔴 Red | <10 Mbps | Slow connections |
| ⚪ Gray | Unknown | Not tested yet |

Click any node to see IP, latency, bandwidth, and connections.

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Your Node      │
│  - Subnet scan  │
│  - Traceroute   │
│  - Bandwidth    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐       ┌─────────────────┐
│   IPFS Network  │◄─────►│  Other Nodes    │
│   - Discovery   │       │  - Contribute   │
│   - Data Share  │       │  - Verify       │
└────────┬────────┘       └─────────────────┘
         │
         ▼
┌─────────────────┐
│  GEXF Files     │
│  - Topology     │
│  - Bandwidth    │
│  - Metadata     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Visualization  │
│  - Web UI       │
│  - Gephi        │
└─────────────────┘
```

### How It Works

1. **Node Startup**: Container launches IPFS daemon + iperf3 server + Python mapper
2. **Subnet Detection**: Automatically identifies your public /24 subnet
3. **Ping Sweep**: Parallel ping (50 workers) finds all live hosts in 2-3 seconds
4. **Traceroute Phase**: Maps paths to:
   - All live subnet hosts
   - Well-known targets (8.8.8.8, 1.1.1.1, root servers, etc.)
   - Other Intermap participants (discovered via IPFS)
5. **Bandwidth Testing**: Sequential iperf3 tests to hosts with port 5201 open
6. **Graph Building**: Hops → nodes, RTT → edge length, bandwidth → edge color
7. **IPFS Publishing**: GEXF files published to IPFS with content-addressed CIDs
8. **Peer Discovery**: Nodes announce presence and discover others via IPFS PubSub
9. **Verification Loop**: Every 5 minutes, ping all mapped IPs to confirm reachability
10. **Web Serving**: React frontend fetches and visualizes aggregated topology

---

## 🤝 Contributing

**Help map the internet!**

### 🌟 Run a Node (Easiest)

Just run the Docker command from Quick Start and leave it running. More nodes = better maps!

### 💻 Code, Bugs, Ideas

- **Code**: See [CONTRIBUTING.md](CONTRIBUTING.md) for developer setup
- **Bugs**: [Open an issue](https://github.com/jaylouisw/intermap/issues)
- **Ideas**: [Start a discussion](https://github.com/jaylouisw/intermap/discussions)

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)**: Simple setup instructions
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Developer guide for code contributions
- **[DEPLOY.md](DEPLOY.md)**: For maintainers deploying to cloud platforms
- **[DEPLOYMENT_INSTRUCTIONS.md](DEPLOYMENT_INSTRUCTIONS.md)**: CI/CD pipeline setup
- **[TESTING.md](TESTING.md)**: Running tests and test coverage

## 🚀 Deployment

### Docker Hub (Recommended)

Pre-built images are automatically published to Docker Hub:

```bash
docker pull jaylouisw/intermap:latest
```

Images are built automatically on every push to master via GitHub Actions.

### Running Your Own Node

**Best results on personal hardware:**
- Home server or desktop PC (Linux recommended)
- Raspberry Pi 4 or similar SBC
- Any system with Docker installed

For development and testing information, see [DEPLOY.md](DEPLOY.md).

---

## 📜 License

**Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**

✅ You are free to:
- **Share**: Copy and redistribute
- **Adapt**: Remix, transform, build upon

❌ Under these terms:
- **Attribution**: Credit Jay Wenden
- **NonCommercial**: No commercial use
- **ShareAlike**: Derivatives must use same license

See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **IPFS**: Decentralized storage and discovery
- **iperf3**: Bandwidth measurement tool
- **vis.js**: Network visualization library
- **Gephi**: Graph analysis software
- **All Contributors**: Thank you for mapping the internet!

---

## � Contact & Community

- **Author**: Jay Wenden
- **GitHub**: [@jaylouisw](https://github.com/jaylouisw)
- **Issues**: [GitHub Issues](https://github.com/jaylouisw/intermap/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jaylouisw/intermap/discussions)
- **Wiki**: [Project Wiki](https://github.com/jaylouisw/intermap/wiki)

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=jaylouisw/intermap&type=Date)](https://star-history.com/#jaylouisw/intermap&Date)

---

**Help us map the internet!** ⭐ Star this repo and run a node today!

- **🔴 Very Slow** (<1 Mbps): Red

