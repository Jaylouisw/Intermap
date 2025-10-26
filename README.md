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

## � Documentation

- **[QUICKSTART.md](QUICKSTART.md)**: Simple setup instructions
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Developer guide
- **[DEPLOY.md](DEPLOY.md)**: For maintainers deploying to cloud platforms
- **[TESTING.md](TESTING.md)**: Running tests

## 🚀 Deployment

### Free Tier Hosting

Deploy Intermap to free cloud platforms:

- **Railway**: [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=...)
- **Render**: One-click deploy from dashboard
- **Fly.io**: Global edge deployment
- **Heroku**: Classic PaaS option

**See [DEPLOY.md](DEPLOY.md) for detailed instructions.**

### Requirements

- **Minimum**: 512 MB RAM, 1 vCPU
- **Recommended**: 1 GB RAM, 2 vCPU
- **Network**: Port 8000 (web), 4001 (IPFS), 5201 (iperf3)
- **Capabilities**: NET_ADMIN, NET_RAW (for traceroute/ping)

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

**Host networking** for accurate topology:- ✅ Install frontend dependencies (npm)

```bash- ✅ Initialize IPFS repository

docker run -d \- ✅ Verify installation

  --network host \

  --cap-add NET_ADMIN \The launcher will:

  --cap-add NET_RAW \- 🚀 Start IPFS daemon

  --name intermap \- 🗺️ Launch Intermap node

  jaylouisw/intermap:latest- 📡 Begin bandwidth testing

```- 🌐 Start web visualizer

- 🌍 **Automatically open browser** to visualizer

**With docker-compose:**

```bashThat's it! Your node is now contributing to the distributed topology map.

curl -O https://raw.githubusercontent.com/jaylouisw/intermap/main/docker-compose.yml

docker-compose up -d### Manual Installation (Advanced)

```

If you prefer manual setup:

### Option 2: Build from Source

1. **Install IPFS**: https://docs.ipfs.io/install/

```bash2. **Install Node.js**: https://nodejs.org/

git clone https://github.com/jaylouisw/intermap.git3. **Setup Python environment**:

cd intermap   ```bash

docker-compose up -d   python -m venv .venv

```   # Activate venv (OS-specific)

   pip install -r requirements.txt

---   ```

4. **Install frontend**:

## 🎯 Usage   ```bash

   cd frontend

### Basic Operation   npm install

   cd ..

1. **Start**: `docker-compose up -d`   ```

2. **Access UI**: http://localhost:80005. **Initialize IPFS**:

3. **View API**: http://localhost:5000   ```bash

4. **IPFS WebUI**: http://localhost:5001/webui   ipfs init

   ```

### Configuration

Then run: `python launch.py`

Edit `config/default.yaml`:

## 🎨 Bandwidth Visualization

```yaml

node:Intermap automatically tests bandwidth between nodes and to public servers using iperf3 and speedtest-cli. Edges are color-coded:

  node_id: "auto"  # Auto-generated unique ID

  update_interval: 300  # Topology update interval (seconds)- **🟢 Gigabit** (≥1 Gbps): Green

  scan_subnet: true- **🟡 Fast** (≥100 Mbps): Yellow-green

  target_subnet: "8.8.8.0/28"  # Subnet to map- **🟠 Medium** (≥10 Mbps): Orange

  max_ips: 256  # Max IPs to scan per subnet- **🔴 Slow** (≥1 Mbps): Red-orange

- **🔴 Very Slow** (<1 Mbps): Red

ipfs:- **⚫ Unknown**: Gray

  api_url: "http://127.0.0.1:5001"

  gateway_url: "http://127.0.0.1:8080"Configuration in `config/default.yaml`:

  rendezvous_key: "intermap-v2-nodes"  # Discovery key```yaml

bandwidth:

traceroute:  enabled: true

  max_hops: 30  iperf3:

  timeout: 2    interval: 7200  # Test every 2 hours

  filter_private: true  # Always filter RFC1918  speedtest:

    interval: 14400  # Test every 4 hours

api:```

  host: "0.0.0.0"

  port: 5000## 🛠️ Manual Operations



ui:### Manual Traceroute

  port: 8000

```Trace a specific public IP:

```bash

### Docker Commandspython src/cli.py trace 8.8.8.8 --output google_route.gexf

```

```bash

# StartTrace an entire subnet (public IPs only):

docker-compose up -d```bash

python src/cli.py subnet 8.8.8.0/28 --output subnet_map.gexf

# View logs```

docker-compose logs -f

**Note**: Private IPs (192.168.x.x, 10.x.x.x, 172.16-31.x.x) are automatically filtered and never included in shared data.

# Stop

docker-compose down### View Topology



# Restart**Option A: Web Viewer (Auto-launched)**

docker-compose restart- Automatically opens at http://localhost:3000

- Interactive graph with bandwidth colors

# Rebuild- Zoom, pan, node selection

docker-compose up -d --build- Bandwidth legend



# View IPFS peers**Option B: Gephi**

docker exec intermap ipfs swarm peers1. Download [Gephi](https://gephi.org/)

```2. Open GEXF files from `output/` directory

3. Use Force Atlas 2 layout for best visualization

---4. Bandwidth data available in edge attributes



## 🔒 Privacy & Security## 📁 Project Structure



### What Gets Shared```

- ✅ Public IP addresses from traceroute hopsIntermap/

- ✅ RTT (latency) measurements├── launch.py           # 🚀 One-command launcher (START HERE!)

- ✅ Bandwidth test results (optional)├── install.py          # 📦 Automated installer

- ✅ Topology graph structure├── src/

│   ├── node/           # Node implementation

### What's Filtered (NEVER Shared)│   │   └── node.py     # Core node logic

- ❌ Private IPs (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)│   ├── traceroute/     # Network path discovery

- ❌ Loopback addresses (127.0.0.0/8)│   │   └── tracer.py   # Traceroute implementation

- ❌ Link-local addresses (169.254.0.0/16)│   ├── ipfs/           # IPFS integration

- ❌ Participant identities│   │   └── client.py   # IPFS client and PubSub

- ❌ Location data│   ├── graph/          # Graph generation

│   │   └── gexf_generator.py  # GEXF file creation

### Security Features│   ├── bandwidth/      # Bandwidth testing

- Automatic private IP filtering in code│   │   └── bandwidth_tester.py  # iperf3 & speedtest

- No identity tracking or logging│   ├── cli.py          # Manual traceroute CLI

- Distributed storage (no central database)│   ├── main.py         # Node entry point

- Open source (verify privacy yourself)│   └── utils.py        # Utility functions

├── config/

---│   └── default.yaml    # Configuration (bandwidth, intervals, etc.)

├── frontend/           # React visualization

## 📊 Data Format│   ├── src/

│   │   ├── components/

### GEXF Graph Structure│   │   │   ├── NetworkGraph.js      # vis.js graph

│   │   │   └── BandwidthLegend.js   # Color legend

```xml│   │   └── utils/

<gexf>│   │       └── gexfLoader.js        # GEXF parser

  <graph mode="static" defaultedgetype="directed">│   └── package.json

    <nodes>├── output/             # Generated GEXF files

      <node id="8.8.8.8" label="8.8.8.8"/>├── tests/              # Unit tests

    </nodes>└── requirements.txt    # Python dependencies

    <edges>```

      <edge source="1.2.3.4" target="8.8.8.8" weight="15.3"/>

    </edges>## 🔧 Configuration

  </graph>

</gexf>Key configuration options in `config/default.yaml`:

```

```yaml

- **Nodes**: Individual IP hops (routers, servers)node:

- **Edges**: Connections between consecutive hops  traceroute:

- **Weights**: RTT in milliseconds    max_hops: 64                     # Deep path discovery (increased from 30)

- **Labels**: IP addresses or reverse DNS if available    timeout: 5                       # Timeout per hop (seconds)

    interval: 300                    # Time between traceroute rounds (5 minutes)

### Analysis with Gephi    auto_map_own_subnet: true       # Automatically map subnet

    subnet_size: 24                  # Subnet to map: /24=254 IPs, /28=14 IPs, /20=4094 IPs

1. Download [Gephi](https://gephi.org/)  rate_limit:

2. Open `output/topology_latest.gexf`    max_traceroutes_per_hour: 0     # Unlimited (0 = no limit)

3. Apply **Force Atlas 2** layout    enable_rate_limiting: false     # Disable rate limiting

4. Color edges by weight (RTT)

5. Analyze centrality, communities, pathsbandwidth:

  enabled: true                      # Enable automatic bandwidth testing

---  iperf3:

    interval: 7200                   # Test every 2 hours

## 🌐 Network Ports  speedtest:

    interval: 14400                  # Test every 4 hours

| Port | Service | Description |  rate_limit:

|------|---------|-------------|    max_tests_per_hour: 5           # Prevent network abuse

| 5000 | API | REST API endpoints |

| 8000 | Web UI | Interactive visualization |ipfs:

| 5001 | IPFS API | IPFS daemon control |  api_address: "/ip4/127.0.0.1/tcp/5001"

| 4001 | IPFS Swarm | P2P connections |  channels:

    discovery: "intermap-discovery"      # Node discovery channel

**Note**: With host networking, container uses these ports directly on host.    topology: "intermap-topology"        # Topology sharing channel

    verification: "intermap-verification"  # Dead IP verification channel

---```



## 🔧 Troubleshooting### Subnet Size Options



### Container won't startChoose based on your network and resources:

```bash

docker-compose logs| Size | IPs | Recommended For | Scan Time |

```|------|-----|----------------|-----------|

| `/28` | 14 | Testing, small networks | ~3 min |

### Port already in use| `/24` | 254 | **Default** - home/business | ~40 min |

Change to bridge networking in `docker-compose.yml`:| `/20` | 4,094 | Large organizations | ~7 hours |

```yaml| `/16` | 65,534 | Enterprise (requires resources) | ~4.5 days |

# Comment out: network_mode: host

# Uncomment ports section**Example configurations**:

ports:```yaml

  - "8001:8000"  # Use different port# Fast & focused (small network)

```subnet_size: 28



### Traceroute not working# Standard (recommended)

Ensure capabilities:subnet_size: 24

```yaml

cap_add:# Comprehensive (large network)

  - NET_ADMINsubnet_size: 20

  - NET_RAWinterval: 600  # Increase interval for large subnets

``````



### IPFS not connecting## 🧪 Development

- Check firewall allows port 4001

- Wait 1-2 minutes for peer discovery### Running Tests

- View peers: `docker exec intermap ipfs swarm peers`

```bash

### Reset everythingpytest tests/ -v

```bash```

docker-compose down -v

docker-compose up -d### Testing Two-Node Setup

```

See [TESTING.md](TESTING.md) for detailed instructions on testing node discovery, traceroute, and bandwidth between two machines on different networks.

---

Quick test:

## 🤝 Contributing```bash

# Machine 1

Contributions welcome! Please:python launch.py



1. Fork the repository# Machine 2 (wait 30s, then run)

2. Create a feature branchpython launch.py

3. Make your changes

4. Submit a pull request# Both should discover each other within 60 seconds

# Check logs for "Discovered new peer"

Please maintain:```

- Privacy-first design (no tracking)

- Distributed architecture (no central servers)### Code Formatting

- CC-BY-NC-SA 4.0 license compliance

```bash

---black src/

flake8 src/

## 📄 License```



**Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International**### Type Checking



Copyright (c) 2025 Jay Wenden```bash

mypy src/

You are free to:```

- Share and redistribute

- Adapt and build upon## 🛡️ Privacy & Security



Under these terms:### Privacy-First Design

- **Attribution**: Credit Jay Wenden

- **NonCommercial**: No commercial use- **No Private IPs**: RFC1918 private addresses (192.168.x.x, 10.x.x.x, 172.16-31.x.x) are automatically filtered and NEVER included in shared data

- **ShareAlike**: Same license for derivatives- **Anonymous Participation**: Nodes do not share identities - only mapping data is exchanged

- **Public IPs Only**: Manual traceroutes reject private IP targets automatically

See [LICENSE](LICENSE) for full terms.- **No Local Network Scanning**: Your local network is never exposed

- **Bandwidth Testing**: Only tests to other consenting nodes and public servers

For commercial licensing, contact Jay Wenden.

## 🚀 Aggressive Mapping Strategy

---

Intermap uses an **aggressive comprehensive mapping strategy** for maximum coverage:

## 🔗 Links

### Automatic Subnet Mapping

- **Docker Hub**: https://hub.docker.com/r/jaylouisw/intermap- Every node automatically maps its entire /24 subnet (254 IPs)

- **GitHub**: https://github.com/jaylouisw/intermap- Example: If your IP is `203.0.113.45`, node maps `203.0.113.1-254`

- **Documentation**: See markdown files in repository- Provides comprehensive coverage of your network's routing perspective

- **Issues**: https://github.com/jaylouisw/intermap/issues

### Multi-Perspective Mapping

---- **No deduplication**: Every node maps every target

- **Why**: Different locations see different routes (Tokyo vs New York)

## 🙏 Acknowledgments- Each node contributes unique routing perspective to global map



Built with:### Collaborative Dead IP Detection

- [IPFS](https://ipfs.tech/) - Distributed file system & P2P networking- Failed traceroutes trigger verification requests to all nodes

- [Kubo](https://github.com/ipfs/kubo) - IPFS implementation- If ≥3 nodes can't reach an IP, it's removed from the map

- [Scapy](https://scapy.net/) - Network packet manipulation- Keeps topology data fresh and accurate

- [React](https://react.dev/) - Frontend framework- Uses dedicated `intermap-verification` IPFS channel

- [vis.js](https://visjs.org/) - Network visualization

- [aiohttp](https://docs.aiohttp.org/) - Async HTTP client/server### Unlimited Traceroutes

- [PyYAML](https://pyyaml.org/) - Configuration management- Rate limiting disabled for comprehensive coverage

- Hop limit increased to 64 (from 30)

---- Traceroute interval reduced to 5 minutes (from 60 minutes)



## 📮 Contact**📖 See [AGGRESSIVE_MAPPING.md](AGGRESSIVE_MAPPING.md) for detailed documentation.**



**Created by Jay Wenden**### Graph Structure



For commercial licensing or inquiries, please open an issue on GitHub.- **Nodes**: Each traceroute hop (router/server) becomes a node in the graph

- **Edges**: Connections between hops with:

---  - RTT (ping time) as latency weight

  - Bandwidth (Mbps) as throughput measure

*Intermap - Mapping the Internet, Together* 🗺️  - Color coding for visual speed indication

- **Weight**: Lower RTT = faster connection, higher bandwidth = thicker/greener edge

### Ethical Considerations

- **Consensual**: Only maps routes between nodes that explicitly join the network
- **Aggressive but Responsible**: High-volume probing may trigger alerts - configure interval if needed
- **Transparent**: All participants are aware they're contributing to comprehensive mapping
- **Public Data**: All shared topology data is publicly visible on IPFS

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **IPFS** for distributed storage infrastructure
- **Gephi** for graph visualization format
- **vis.js** for interactive web graphs
- **iperf3** and **speedtest-cli** for bandwidth testing
- All contributors to the distributed topology map

## 📞 Support

- **Issues**: https://github.com/your-repo/intermap/issues
- **Documentation**: See README.md (this file)
- **Discussions**: https://github.com/your-repo/intermap/discussions

---

**Made with ❤️ by the distributed mapping community**

### Security Notes

- Traceroute requires elevated privileges (administrator/root)
- IPFS data is public - topology maps are visible to everyone
- Node identities are not shared - only mapping data
- All traceroute data contains only public IP addresses
- Private networks are protected by automatic filtering

## 🤝 Contributing

Contributions welcome! Areas for development:

- [ ] Complete traceroute parser implementations
- [ ] Finish IPFS PubSub integration
- [ ] Build React frontend with vis.js
- [ ] Add data aggregation/merging logic
- [ ] Implement peer reputation system
- [ ] Add geographic IP location data
- [ ] Create real-time topology updates
- [ ] Optimize GEXF file sizes for large graphs

## 📄 License

MIT License - See LICENSE file for details

## 🔗 Resources

- [Gephi Graph Visualization](https://gephi.org/)
- [GEXF Format Specification](https://gexf.net/)
- [IPFS Documentation](https://docs.ipfs.io/)
- [Scapy Network Tool](https://scapy.net/)
- [vis.js Network](https://visjs.org/)

## 🐛 Known Issues

- Windows tracert parsing not yet implemented
- Unix traceroute parsing not yet implemented  
- IPFS PubSub integration incomplete
- Frontend not yet built
- No data persistence beyond IPFS

## 📞 Contact

For questions or collaboration: [Your Contact Info]

---

**Status**: 🚧 Early Development - Core structure in place, implementations in progress

