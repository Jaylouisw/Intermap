<!--
Intermap - Testing Guide
Copyright (c) 2025 Jay Wenden
Licensed under CC-BY-NC-SA 4.0
-->

# Intermap Testing Guide

*Created by Jay Wenden*

---

## Testing Node Discovery and Traceroute

This guide explains how to test Intermap with two nodes on different networks.

## Prerequisites

- Two computers on different networks (different locations, different ISPs)
- Docker installed on both
- Python 3.9+ and all dependencies installed on both
- Administrator/sudo privileges for traceroute

## Setup Instructions

### On Both Machines:

1. **Install Intermap**:
   ```bash
   python install.py
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate  # Windows
   ```

2. **Verify IPFS is running**:
   ```bash
   ipfs daemon
   ```
   
   Leave this running in a separate terminal.

3. **Check connectivity**:
   ```bash
   python -c "from src.nat_detection import test_connectivity; import json; print(json.dumps(test_connectivity(), indent=2))"
   ```
   
   This will show:
   - Your local IP
   - Your external IP
   - Whether you're behind NAT
   - If traceroute works
   - If iperf3 port is open

## Running Tests

### Test 1: Single Node (Baseline)

On one machine:
```bash
python launch.py
```

Expected behavior:
- ✅ IPFS daemon connects
- ✅ Node announces presence
- ✅ Shows "No peers discovered yet, waiting..."
- ✅ Frontend opens in browser showing "0 peers"
- ✅ After a few minutes, shows "No topology data available yet"

This is normal for a single node - it needs a peer to traceroute to.

### Test 2: Two Nodes (Full Test)

On **Machine A**:
```bash
python launch.py
```

On **Machine B** (wait 30 seconds after A starts):
```bash
python launch.py
```

Expected sequence:

**After ~30-60 seconds**:
- Both nodes should log: `Discovered new peer: node-XXXX @ <IP>`
- Both nodes should show: `Known peers: 1`

**After ~2-5 minutes** (first traceroute):
- Log: `Tracing route to peer: node-XXXX @ <IP>`
- Log: `Traceroute complete: N hops to node-XXXX`
- Log: `Published topology to IPFS: <CID>`
- Frontend should now show nodes and connections!

**After ~30-60 minutes** (first bandwidth test):
- Log: `Running iperf3 bandwidth tests...`
- Log: `iperf3 to X.X.X.X: Y.Y Mbps down, Z.Z Mbps up`
- Edges in frontend should become color-coded

## Troubleshooting

### "No peers discovered"

Check IPFS connectivity:
```bash
ipfs swarm peers
```

If no peers shown, IPFS may be firewalled. Try:
```bash
ipfs swarm connect /ip4/104.131.131.82/tcp/4001/p2p/QmaCpDMGvV2BGHeYERUEnRQAwe3N8SzbUtfsmvsqQLuvuJ
```

### "Traceroute not working"

- **Windows**: Run PowerShell as Administrator
- **Linux/Mac**: Run with `sudo python launch.py`
- Or: Disable traceroute and just test discovery:
  ```yaml
  # In config/default.yaml
  node:
    traceroute:
      enabled: false
  ```

### "Behind NAT"

This is normal. NAT doesn't prevent discovery or outgoing traceroutes.

However, incoming bandwidth tests may fail. To allow:
- **Port forward 5201** on your router to your machine
- Or use UPnP if available

### "External IP changed"

Nodes detect IP changes automatically and re-announce. Check logs for:
```
External IP changed: <old> -> <new>
```

## Verification Checklist

✅ **Discovery Working**:
- Both nodes log "Discovered new peer"
- `Known peers: 1` on both

✅ **Traceroute Working**:
- Logs show "Tracing route to peer"
- Logs show "Traceroute complete: N hops"
- GEXF files appear in `output/` directory

✅ **IPFS Working**:
- Logs show "Published topology to IPFS: Qm..."
- Both nodes can see each other's topology updates

✅ **Frontend Working**:
- Browser opens automatically to http://localhost:3000
- Graph shows nodes and edges
- Stats show correct counts
- Edges have colors (after bandwidth tests)

✅ **Bandwidth Testing**:
- After ~1 hour, logs show "Running iperf3 bandwidth tests"
- After ~4 hours, logs show "Running speedtest"
- Edges in graph change color based on speed

## Expected Logs

**Good logs to see**:
```
✓ Connected to IPFS at /ip4/127.0.0.1/tcp/5001 (version: X.X.X)
✓ Intermap node started successfully
External IP: X.X.X.X
Announced presence: node-abc123 @ X.X.X.X
Discovered new peer: node-def456 @ Y.Y.Y.Y
Tracing route to peer: node-def456 @ Y.Y.Y.Y
Traceroute complete: 12 hops to node-def456
Published topology to IPFS: QmXXXXX
```

**Normal warnings**:
```
⚠ Behind NAT: Local 192.168.1.100 -> External X.X.X.X
⚠ iperf3 port (5201) not reachable
```

**Bad errors**:
```
❌ Failed to connect to IPFS
❌ No internet connectivity detected
❌ Traceroute failed to node-XXX
```

## Manual Testing

### Test Discovery Without Traceroute

```python
import asyncio
from src.node.node import TopologyNode

async def test():
    node = TopologyNode()
    await node.start()
    
    # Wait for discovery
    await asyncio.sleep(60)
    
    print(f"Discovered {len(node.peer_nodes)} peers:")
    for peer_id, peer_info in node.peer_nodes.items():
        print(f"  {peer_id}: {peer_info.external_ip}")
    
    await node.stop()

asyncio.run(test())
```

### Test Traceroute to Known IP

```bash
python src/cli.py trace 8.8.8.8 --output test_google.gexf
```

Should create a GEXF file with the route to Google DNS.

## Success Criteria

🎉 **Full Success**:
- Two nodes on different networks
- Both discover each other within 60 seconds
- Both complete traceroutes within 5 minutes
- Both see each other's topology on IPFS
- Frontend shows the network graph with both paths
- After 1-2 hours, edges are color-coded by bandwidth

## Getting Help

If tests fail, include in your report:
1. Output of `python src/nat_detection.py`
2. Relevant log excerpts from both nodes
3. Output of `ipfs swarm peers` on both nodes
4. Network topology (same LAN? Different ISPs? VPN?)

---

**Note**: First discovery between two nodes on the internet can take 1-2 minutes due to IPFS peer discovery. Be patient!

