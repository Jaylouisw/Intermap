# Intermap - Distributed Internet Topology Mapper

A distributed computing project that creates a collaborative, browsable map of internet infrastructure. Participant nodes perform **aggressive comprehensive mapping** of their network subnets, with collaborative dead IP detection and multi-perspective routing analysis.

## 🌐 Project Overview

**Intermap** enables consenting participants to collaboratively map internet infrastructure by:
- Running anonymous nodes that discover other participants via IPFS
- **Automatically mapping entire /24 subnet** of each node's public IP
- Performing continuous traceroutes with **no rate limiting or hop limits**
- **Multi-perspective mapping**: Every node maps every target for different routing perspectives
- **Collaborative dead IP detection**: Nodes verify and remove unreachable IPs via consensus
- Each traceroute hop becomes a node, ping speed (RTT) becomes the edge weight
- Bandwidth measurements color-code connections (green=gigabit, red=very slow)
- **Privacy-first**: Only public IPs are shared - private IPs are NEVER included
- **Anonymity**: Nodes share only mapping data, not participant identities
- Storing topology data on IPFS for distributed, censorship-resistant storage
- Generating GEXF files compatible with Gephi for advanced visualization
- Providing a web-based visualization using React and vis.js with bandwidth legends

**Key Principles**:
- ✅ Only public IPs (RFC1918 private ranges filtered)
- ✅ Anonymous participation (no identity sharing)
- ✅ Aggressive comprehensive mapping (entire subnets)
- ✅ Multi-perspective routing (no deduplication)
- ✅ Collaborative verification (dead IP detection)
- ✅ Distributed storage (IPFS)
- ✅ Bandwidth visualization (color-coded by speed)

## 🏗️ Architecture

```
┌─────────────────┐
│  Participant    │
│     Node        │◄─────┐
│  (Your PC)      │      │
└────────┬────────┘      │
         │               │
         │ Traceroute    │ IPFS
         │ + Bandwidth   │ PubSub
         ▼               │
┌─────────────────┐      │
│  Participant    │      │
│     Node        │◄─────┤
│   (Other PC)    │      │
└────────┬────────┘      │
         │               │
         └───────────────┘
                │
                ▼
         ┌──────────┐
         │   IPFS   │
         │ Network  │
         └────┬─────┘
              │
              ▼
      ┌──────────────┐
      │ GEXF Files   │
      │ (Graphs with │
      │  Bandwidth)  │
      └──────┬───────┘
              │
       ┌──────┴───────┐
       │              │
       ▼              ▼
  ┌────────┐    ┌──────────┐
  │ Gephi  │    │   Web    │
  │Software│    │  Viewer  │
  └────────┘    └──────────┘
```

## 📋 Prerequisites

- **Python 3.9+**
- **IPFS Desktop or IPFS Daemon** - [Install IPFS](https://docs.ipfs.io/install/)
- **Node.js 16+** - [Install Node.js](https://nodejs.org/)
- **Optional**: iperf3 and speedtest-cli for bandwidth testing

## 🚀 Quick Start

### One-Command Installation

**Windows:**
```powershell
python install.py
.venv\Scripts\activate
python launch.py
```

**Linux/Mac:**
```bash
python3 install.py
source .venv/bin/activate
python3 launch.py
```

The installer will:
- ✅ Check Python version and system dependencies
- ✅ Create virtual environment
- ✅ Install all Python packages
- ✅ Install frontend dependencies (npm)
- ✅ Initialize IPFS repository
- ✅ Verify installation

The launcher will:
- 🚀 Start IPFS daemon
- 🗺️ Launch Intermap node
- 📡 Begin bandwidth testing
- 🌐 Start web visualizer
- 🌍 **Automatically open browser** to visualizer

That's it! Your node is now contributing to the distributed topology map.

### Manual Installation (Advanced)

If you prefer manual setup:

1. **Install IPFS**: https://docs.ipfs.io/install/
2. **Install Node.js**: https://nodejs.org/
3. **Setup Python environment**:
   ```bash
   python -m venv .venv
   # Activate venv (OS-specific)
   pip install -r requirements.txt
   ```
4. **Install frontend**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```
5. **Initialize IPFS**:
   ```bash
   ipfs init
   ```

Then run: `python launch.py`

## 🎨 Bandwidth Visualization

Intermap automatically tests bandwidth between nodes and to public servers using iperf3 and speedtest-cli. Edges are color-coded:

- **🟢 Gigabit** (≥1 Gbps): Green
- **🟡 Fast** (≥100 Mbps): Yellow-green
- **🟠 Medium** (≥10 Mbps): Orange
- **🔴 Slow** (≥1 Mbps): Red-orange
- **🔴 Very Slow** (<1 Mbps): Red
- **⚫ Unknown**: Gray

Configuration in `config/default.yaml`:
```yaml
bandwidth:
  enabled: true
  iperf3:
    interval: 7200  # Test every 2 hours
  speedtest:
    interval: 14400  # Test every 4 hours
```

## 🛠️ Manual Operations

### Manual Traceroute

Trace a specific public IP:
```bash
python src/cli.py trace 8.8.8.8 --output google_route.gexf
```

Trace an entire subnet (public IPs only):
```bash
python src/cli.py subnet 8.8.8.0/28 --output subnet_map.gexf
```

**Note**: Private IPs (192.168.x.x, 10.x.x.x, 172.16-31.x.x) are automatically filtered and never included in shared data.

### View Topology

**Option A: Web Viewer (Auto-launched)**
- Automatically opens at http://localhost:3000
- Interactive graph with bandwidth colors
- Zoom, pan, node selection
- Bandwidth legend

**Option B: Gephi**
1. Download [Gephi](https://gephi.org/)
2. Open GEXF files from `output/` directory
3. Use Force Atlas 2 layout for best visualization
4. Bandwidth data available in edge attributes

## 📁 Project Structure

```
Intermap/
├── launch.py           # 🚀 One-command launcher (START HERE!)
├── install.py          # 📦 Automated installer
├── src/
│   ├── node/           # Node implementation
│   │   └── node.py     # Core node logic
│   ├── traceroute/     # Network path discovery
│   │   └── tracer.py   # Traceroute implementation
│   ├── ipfs/           # IPFS integration
│   │   └── client.py   # IPFS client and PubSub
│   ├── graph/          # Graph generation
│   │   └── gexf_generator.py  # GEXF file creation
│   ├── bandwidth/      # Bandwidth testing
│   │   └── bandwidth_tester.py  # iperf3 & speedtest
│   ├── cli.py          # Manual traceroute CLI
│   ├── main.py         # Node entry point
│   └── utils.py        # Utility functions
├── config/
│   └── default.yaml    # Configuration (bandwidth, intervals, etc.)
├── frontend/           # React visualization
│   ├── src/
│   │   ├── components/
│   │   │   ├── NetworkGraph.js      # vis.js graph
│   │   │   └── BandwidthLegend.js   # Color legend
│   │   └── utils/
│   │       └── gexfLoader.js        # GEXF parser
│   └── package.json
├── output/             # Generated GEXF files
├── tests/              # Unit tests
└── requirements.txt    # Python dependencies
```

## 🔧 Configuration

Key configuration options in `config/default.yaml`:

```yaml
node:
  traceroute:
    max_hops: 64                     # Deep path discovery (increased from 30)
    timeout: 5                       # Timeout per hop (seconds)
    interval: 300                    # Time between traceroute rounds (5 minutes)
    auto_map_own_subnet: true       # Automatically map subnet
    subnet_size: 24                  # Subnet to map: /24=254 IPs, /28=14 IPs, /20=4094 IPs
  rate_limit:
    max_traceroutes_per_hour: 0     # Unlimited (0 = no limit)
    enable_rate_limiting: false     # Disable rate limiting

bandwidth:
  enabled: true                      # Enable automatic bandwidth testing
  iperf3:
    interval: 7200                   # Test every 2 hours
  speedtest:
    interval: 14400                  # Test every 4 hours
  rate_limit:
    max_tests_per_hour: 5           # Prevent network abuse

ipfs:
  api_address: "/ip4/127.0.0.1/tcp/5001"
  channels:
    discovery: "intermap-discovery"      # Node discovery channel
    topology: "intermap-topology"        # Topology sharing channel
    verification: "intermap-verification"  # Dead IP verification channel
```

### Subnet Size Options

Choose based on your network and resources:

| Size | IPs | Recommended For | Scan Time |
|------|-----|----------------|-----------|
| `/28` | 14 | Testing, small networks | ~3 min |
| `/24` | 254 | **Default** - home/business | ~40 min |
| `/20` | 4,094 | Large organizations | ~7 hours |
| `/16` | 65,534 | Enterprise (requires resources) | ~4.5 days |

**Example configurations**:
```yaml
# Fast & focused (small network)
subnet_size: 28

# Standard (recommended)
subnet_size: 24

# Comprehensive (large network)
subnet_size: 20
interval: 600  # Increase interval for large subnets
```

## 🧪 Development

### Running Tests

```bash
pytest tests/ -v
```

### Testing Two-Node Setup

See [TESTING.md](TESTING.md) for detailed instructions on testing node discovery, traceroute, and bandwidth between two machines on different networks.

Quick test:
```bash
# Machine 1
python launch.py

# Machine 2 (wait 30s, then run)
python launch.py

# Both should discover each other within 60 seconds
# Check logs for "Discovered new peer"
```

### Code Formatting

```bash
black src/
flake8 src/
```

### Type Checking

```bash
mypy src/
```

## 🛡️ Privacy & Security

### Privacy-First Design

- **No Private IPs**: RFC1918 private addresses (192.168.x.x, 10.x.x.x, 172.16-31.x.x) are automatically filtered and NEVER included in shared data
- **Anonymous Participation**: Nodes do not share identities - only mapping data is exchanged
- **Public IPs Only**: Manual traceroutes reject private IP targets automatically
- **No Local Network Scanning**: Your local network is never exposed
- **Bandwidth Testing**: Only tests to other consenting nodes and public servers

## 🚀 Aggressive Mapping Strategy

Intermap uses an **aggressive comprehensive mapping strategy** for maximum coverage:

### Automatic Subnet Mapping
- Every node automatically maps its entire /24 subnet (254 IPs)
- Example: If your IP is `203.0.113.45`, node maps `203.0.113.1-254`
- Provides comprehensive coverage of your network's routing perspective

### Multi-Perspective Mapping
- **No deduplication**: Every node maps every target
- **Why**: Different locations see different routes (Tokyo vs New York)
- Each node contributes unique routing perspective to global map

### Collaborative Dead IP Detection
- Failed traceroutes trigger verification requests to all nodes
- If ≥3 nodes can't reach an IP, it's removed from the map
- Keeps topology data fresh and accurate
- Uses dedicated `intermap-verification` IPFS channel

### Unlimited Traceroutes
- Rate limiting disabled for comprehensive coverage
- Hop limit increased to 64 (from 30)
- Traceroute interval reduced to 5 minutes (from 60 minutes)

**📖 See [AGGRESSIVE_MAPPING.md](AGGRESSIVE_MAPPING.md) for detailed documentation.**

### Graph Structure

- **Nodes**: Each traceroute hop (router/server) becomes a node in the graph
- **Edges**: Connections between hops with:
  - RTT (ping time) as latency weight
  - Bandwidth (Mbps) as throughput measure
  - Color coding for visual speed indication
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
