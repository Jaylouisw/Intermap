# Intermap - Distributed Internet Topology Mapper - Copilot Instructions

## Project Overview
**Intermap** is a distributed computing project that maps internet infrastructure. Participant nodes perform traceroutes where each hop becomes a node and ping speed (RTT) becomes the edge weight, creating a collaborative network topology visualization.

## Technology Stack
- **Backend**: Python 3.9+
- **Distributed Storage**: IPFS
- **Coordination**: IPFS PubSub
- **Graph Format**: GEXF (Gephi Exchange Format) with RTT edge weights
- **Frontend**: React with vis.js OR Gephi software
- **Network Tools**: scapy, traceroute utilities

## Architecture
- Anonymous nodes discover each other via IPFS PubSub
- Nodes perform traceroutes to other participants OR manually to public IPs/subnets
- Each traceroute hop = node, RTT = edge weight
- Only public IPs shared (RFC1918 private IPs filtered automatically)
- Topology data stored as GEXF files on IPFS
- Web frontend visualizes aggregated network graph
- Gephi-compatible export for offline analysis

## Graph Structure
- **Nodes**: Individual hops in traceroutes (routers, servers)
- **Edges**: Connections between consecutive hops
- **Edge Weight**: RTT (round-trip time) in milliseconds

## Privacy & Security
- **CRITICAL**: Only public IPs are included - private IPs NEVER shared
- **Anonymity**: Nodes share only mapping data, not participant identities
- Filter RFC1918 addresses: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
- Also filter loopback, link-local, and reserved ranges
- Manual traceroutes reject private IP targets
- Subnet scans limited to 256 IPs maximum

## Development Guidelines
- Follow PEP 8 for Python code
- Use async/await for IPFS operations
- Always filter private IPs before sharing data
- Implement proper error handling for network operations
- Store configuration in YAML files
- Use logging extensively for debugging distributed operations
- Write modular, testable code

## Security Considerations
- Validate all data received from IPFS
- Never include private IP addresses in public data

