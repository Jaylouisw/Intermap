<!--# Intermap - Distributed Internet Topology Mapper

Intermap - Distributed P2P Internet Topology Mapper

Copyright (c) 2025 Jay WendenA distributed computing project that creates a collaborative, browsable map of internet infrastructure. Participant nodes perform **aggressive comprehensive mapping** of their network subnets, with collaborative dead IP detection and multi-perspective routing analysis.

Licensed under CC-BY-NC-SA 4.0

-->## 🌐 Project Overview



# Intermap**Intermap** enables consenting participants to collaboratively map internet infrastructure by:

- Running anonymous nodes that discover other participants via IPFS

**Distributed P2P Internet Topology Mapper**- **Automatically mapping entire /24 subnet** of each node's public IP

- Performing continuous traceroutes with **no rate limiting or hop limits**

[![Docker Build](https://github.com/YOUR_USERNAME/intermap/actions/workflows/docker-build.yml/badge.svg)](https://github.com/YOUR_USERNAME/intermap/actions/workflows/docker-build.yml)- **Multi-perspective mapping**: Every node maps every target for different routing perspectives

[![Docker Hub](https://img.shields.io/docker/pulls/YOUR_USERNAME/intermap)](https://hub.docker.com/r/YOUR_USERNAME/intermap)- **Collaborative dead IP detection**: Nodes verify and remove unreachable IPs via consensus

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)- Each traceroute hop becomes a node, ping speed (RTT) becomes the edge weight

- Bandwidth measurements color-code connections (green=gigabit, red=very slow)

*Created by Jay Wenden*- **Privacy-first**: Only public IPs are shared - private IPs are NEVER included

- **Anonymity**: Nodes share only mapping data, not participant identities

Intermap is a fully distributed computing project that creates collaborative maps of internet infrastructure. Participants run nodes that perform traceroutes, with each hop becoming a node and RTT (round-trip time) becoming the edge weight in a shared network topology graph.- Storing topology data on IPFS for distributed, censorship-resistant storage

- Generating GEXF files compatible with Gephi for advanced visualization

---- Providing a web-based visualization using React and vis.js with bandwidth legends



## 🚀 Quick Start**Key Principles**:

- ✅ Only public IPs (RFC1918 private ranges filtered)

**Requires only Docker:**- ✅ Anonymous participation (no identity sharing)

- ✅ Aggressive comprehensive mapping (entire subnets)

```bash- ✅ Multi-perspective routing (no deduplication)

# Host networking (recommended - most accurate)- ✅ Collaborative verification (dead IP detection)

docker run -d \- ✅ Distributed storage (IPFS)

  --network host \- ✅ Bandwidth visualization (color-coded by speed)

  --cap-add NET_ADMIN \

  --cap-add NET_RAW \## 🏗️ Architecture

  --name intermap \

  YOUR_USERNAME/intermap:latest```

```┌─────────────────┐

│  Participant    │

Access the web UI at **http://localhost:8000**│     Node        │◄─────┐

│  (Your PC)      │      │

---└────────┬────────┘      │

         │               │

## ✨ Features         │ Traceroute    │ IPFS

         │ + Bandwidth   │ PubSub

### Fully Distributed Architecture         ▼               │

- **Pure P2P**: IPFS-based coordination with no central server┌─────────────────┐      │

- **Content Addressing**: Nodes announce via CIDs, discover through DHT│  Participant    │      │

- **Collaborative**: All participants contribute to shared topology│     Node        │◄─────┤

- **Resilient**: No single point of failure│   (Other PC)    │      │

└────────┬────────┘      │

### Privacy & Security         │               │

- **Privacy First**: Only public IPs shared (RFC1918 private addresses filtered)         └───────────────┘

- **Anonymous**: No identity data collected from participants                │

- **Automatic Filtering**: 10.x, 172.16.x, 192.168.x automatically excluded                ▼

- **Transparent**: Open source, verifiable privacy         ┌──────────┐

         │   IPFS   │

### Network Mapping         │ Network  │

- **Traceroute**: Discovers network paths hop-by-hop         └────┬─────┘

- **RTT Weighting**: Edge weights based on round-trip time              │

- **Bandwidth Testing**: Optional iperf3 bandwidth measurements              ▼

- **Real-time**: Live topology updates as nodes map      ┌──────────────┐

      │ GEXF Files   │

### Visualization & Export      │ (Graphs with │

- **Interactive Graph**: Real-time network visualization with vis.js      │  Bandwidth)  │

- **Color Coding**: Bandwidth/RTT-based edge coloring      └──────┬───────┘

- **GEXF Export**: Compatible with Gephi for advanced analysis              │

- **Node Highlighting**: Click to inspect individual hops       ┌──────┴───────┐

       │              │

---       ▼              ▼

  ┌────────┐    ┌──────────┐

## 🏗️ Architecture  │ Gephi  │    │   Web    │

  │Software│    │  Viewer  │

```  └────────┘    └──────────┘

┌─────────────────┐       ┌──────────────┐```

│   Node A        │       │     IPFS     │

│  (Windows/Mac)  │◄─────►│   Network    │## 📋 Prerequisites

│  - Traceroute   │       │    (DHT)     │

│  - Bandwidth    │       └──────────────┘- **Python 3.9+**

└─────────────────┘             ▲- **IPFS Desktop or IPFS Daemon** - [Install IPFS](https://docs.ipfs.io/install/)

                                │- **Node.js 16+** - [Install Node.js](https://nodejs.org/)

┌─────────────────┐             │- **Optional**: iperf3 and speedtest-cli for bandwidth testing

│   Node B        │             │

│    (Linux)      │◄────────────┘## 🚀 Quick Start

│  - Traceroute   │

│  - Bandwidth    │### One-Command Installation

└─────────────────┘

```**Windows:**

```powershell

### How It Workspython install.py

.venv\Scripts\activate

1. **Node Announcement**: Each node publishes its info to IPFS as a CIDpython launch.py

2. **Peer Discovery**: Nodes find each other via IPFS DHT and swarm queries```

3. **Network Mapping**: Nodes perform traceroutes to targets/other nodes

4. **Data Sharing**: Topology data published to IPFS with pinning**Linux/Mac:**

5. **Aggregation**: Frontend fetches and merges all topologies into unified graph```bash

python3 install.py

**No central server required!** Everything runs peer-to-peer through IPFS.source .venv/bin/activate

python3 launch.py

---```



## 📦 InstallationThe installer will:

- ✅ Check Python version and system dependencies

### Option 1: Docker (Recommended)- ✅ Create virtual environment

- ✅ Install all Python packages

**Host networking** for accurate topology:- ✅ Install frontend dependencies (npm)

```bash- ✅ Initialize IPFS repository

docker run -d \- ✅ Verify installation

  --network host \

  --cap-add NET_ADMIN \The launcher will:

  --cap-add NET_RAW \- 🚀 Start IPFS daemon

  --name intermap \- 🗺️ Launch Intermap node

  YOUR_USERNAME/intermap:latest- 📡 Begin bandwidth testing

```- 🌐 Start web visualizer

- 🌍 **Automatically open browser** to visualizer

**With docker-compose:**

```bashThat's it! Your node is now contributing to the distributed topology map.

curl -O https://raw.githubusercontent.com/YOUR_USERNAME/intermap/main/docker-compose.yml

docker-compose up -d### Manual Installation (Advanced)

```

If you prefer manual setup:

### Option 2: Build from Source

1. **Install IPFS**: https://docs.ipfs.io/install/

```bash2. **Install Node.js**: https://nodejs.org/

git clone https://github.com/YOUR_USERNAME/intermap.git3. **Setup Python environment**:

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

- **Docker Hub**: https://hub.docker.com/r/YOUR_USERNAME/intermap- Every node automatically maps its entire /24 subnet (254 IPs)

- **GitHub**: https://github.com/YOUR_USERNAME/intermap- Example: If your IP is `203.0.113.45`, node maps `203.0.113.1-254`

- **Documentation**: See markdown files in repository- Provides comprehensive coverage of your network's routing perspective

- **Issues**: https://github.com/YOUR_USERNAME/intermap/issues

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
