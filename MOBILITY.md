<!--
Intermap - Distributed P2P Internet Topology Mapper
Copyright (c) 2025 Jay Wenden
Licensed under CC-BY-NC-SA 4.0
-->

# Mobility Support - Moving Devices & IP Changes

## Overview
Intermap fully supports **mobile and portable devices** that change their network location and IP address, including:
- 📱 **Mobile phones** (switching cell towers, WiFi networks)
- 🛰️ **Satellites** (changing ground stations as they orbit)
- 💻 **Laptops** (moving between WiFi networks, 5G, ethernet)
- 🚗 **Vehicle-based devices** (cars, buses, trains with mobile internet)
- ✈️ **Aircraft connectivity** (in-flight WiFi changing connections)

## How It Works

### 1. IP Change Detection
Every 60 seconds (configurable), the node checks if its external IP has changed:

```python
# _heartbeat_loop() in node.py
new_ip = self._get_external_ip()
if new_ip and new_ip != self.external_ip:
    logger.warning(f"🚀 MOBILITY DETECTED: {old_ip} -> {new_ip}")
    await self._handle_mobility(old_ip, new_ip)
```

### 2. Mobility Handling Process

When IP change is detected, the node automatically:

#### Step 1: Remove Old Subnet Targets
- Calculates old /24 subnet (e.g., `203.0.113.0/24`)
- Removes all old subnet IPs from `trace_targets`
- Stops tracing old location's IPs

#### Step 2: Add New Subnet Targets
- Calculates new /24 subnet (e.g., `198.51.100.0/24`)
- Adds all 254 new subnet IPs to `trace_targets`
- Begins tracing new location's network

#### Step 3: Track Mobility Events
- Records IP change with timestamp
- Maintains history of last 10 mobility events
- Includes mobility metadata in topology data

#### Step 4: Optional Cleanup
- Can optionally remove old location data from graph
- Default: Keep historical data to show movement path
- Configurable via `mobility.cleanup_old_location` setting

### 3. Re-announcement
After handling mobility, the node:
- Re-announces presence on IPFS discovery channel
- Other nodes update their peer list with new IP
- Traceroutes from peers will use new IP

## Configuration

### Mobility Settings (`config/default.yaml`)
```yaml
node:
  mobility:
    cleanup_old_location: false  # Keep historical path data (true = clean up)
    detect_interval: 60  # Seconds between IP checks (heartbeat interval)
```

### Detection Interval
- **Default**: 60 seconds (fast enough for most use cases)
- **Mobile phones**: Consider 30 seconds for frequent tower switching
- **Satellites**: 60-120 seconds (ground station changes less frequent)
- **Laptops**: 60 seconds (adequate for WiFi switching)

## Use Cases

### 📱 Mobile Phone on Cellular Network
**Scenario**: User driving, phone switching between cell towers

**Behavior**:
1. Phone connects to Tower A: `203.0.113.45`
2. Maps subnet: `203.0.113.0/24`
3. 10 minutes later, switches to Tower B: `198.51.100.78`
4. **MOBILITY DETECTED** - removes old subnet, maps new subnet: `198.51.100.0/24`
5. Continues mapping from new location

**Logs**:
```
INFO - External IP: 203.0.113.45
INFO - Added 254 IPs from own subnet 203.0.113.0/24 to trace targets
...
WARNING - 🚀 MOBILITY DETECTED: 203.0.113.45 -> 198.51.100.78
INFO - 🔄 Handling mobility: 203.0.113.45 -> 198.51.100.78
INFO - Removed 254 old subnet targets from 203.0.113.0/24
INFO - Added 254 new subnet targets for 198.51.100.78/24
INFO - ✅ Mobility handling complete - now mapping from new location
INFO - Total mobility events: 1
```

### 🛰️ Satellite in Orbit
**Scenario**: LEO satellite changing ground stations every 5-10 minutes

**Behavior**:
1. Connects via Ground Station 1 (New York): `192.0.2.100`
2. Maps regional subnet: `192.0.2.0/24`
3. Orbit moves satellite out of range
4. Connects via Ground Station 2 (London): `198.51.100.200`
5. **MOBILITY DETECTED** - remaps new region: `198.51.100.0/24`
6. Process repeats every orbit

**Special Consideration**: High-frequency mobility
- With 60s detection, satellite could change IPs every minute
- Consider increasing `detect_interval` to 120s for satellites
- Historical data shows orbital path through different subnets

### 💻 Laptop Moving Between Networks
**Scenario**: User with laptop moving from home WiFi → coffee shop WiFi → mobile hotspot

**Timeline**:
- **08:00** - Home WiFi: `192.0.2.50` → Maps `192.0.2.0/24`
- **09:30** - Coffee shop: `198.51.100.150` → **MOBILITY** → Maps `198.51.100.0/24`
- **12:00** - Mobile hotspot: `203.0.113.75` → **MOBILITY** → Maps `203.0.113.0/24`

**Result**: Laptop contributes mapping data from 3 different network perspectives in one day!

### 🚗 Vehicle with Mobile Internet
**Scenario**: Bus with onboard WiFi traveling across country

**Behavior**:
- Constantly switching between cell towers along route
- Might change IPs every few kilometers
- High mobility frequency
- Each IP change = new subnet mapping = comprehensive route coverage

**Benefit**: Single bus can map hundreds of subnets along its route, providing unique mobile perspective of network infrastructure.

## Mobility Event Tracking

### Data Structure
```python
self.mobility_events = [
    {
        "timestamp": "2024-10-24T10:30:00Z",
        "old_ip": "203.0.113.45",
        "new_ip": "198.51.100.78",
        "reason": "ip_change_detected"
    },
    # ... up to 10 most recent events
]
```

### Viewing Mobility History
Mobility events are saved to `output/node_info.json`:
```json
{
  "external_ip": "198.51.100.78",
  "node_id": "abc123...",
  "timestamp": "2024-10-24T10:35:00Z",
  "mobility_events": [
    {
      "timestamp": "2024-10-24T10:30:00Z",
      "old_ip": "203.0.113.45",
      "new_ip": "198.51.100.78",
      "reason": "ip_change_detected"
    }
  ]
}
```

## Graph Data & Historical Paths

### Keep Historical Data (Default)
**Setting**: `mobility.cleanup_old_location: false`

**Behavior**:
- Node keeps all mapped data from previous locations
- Graph shows complete path of device movement
- Useful for visualizing mobile device routing over time

**Example**: Laptop that moved through 3 networks shows:
```
Home Subnet (192.0.2.0/24) → Coffee Shop Subnet (198.51.100.0/24) → Mobile Hotspot (203.0.113.0/24)
```

### Clean Up Old Data
**Setting**: `mobility.cleanup_old_location: true`

**Behavior**:
- Node removes old subnet data when IP changes
- Only current location data retained
- Reduces graph size for high-mobility devices

**Use Case**: Satellite that changes IPs every 5 minutes - without cleanup, graph would grow massive with stale data.

## Performance Considerations

### High-Frequency Mobility
**Problem**: Device changing IPs every 1-2 minutes

**Impact**:
- Constant subnet remapping overhead
- Many incomplete traceroutes (interrupted by IP change)
- Rapid IPFS re-announcements

**Solutions**:
1. Increase `detect_interval` to reduce checking frequency
2. Enable `cleanup_old_location` to prevent graph bloat
3. Reduce `interval` (traceroute cycle) so more traces complete before IP changes

### Low-Frequency Mobility
**Problem**: Device rarely changes IPs (e.g., laptop at home)

**Impact**: Minimal - just extra IP checks every 60 seconds

**Optimization**: Default settings already optimal

## Visualizer Integration

### Own Node Highlighting
Your node's current IP is **highlighted in magenta** in the web visualizer:

**Features**:
- ⭐ **Bright magenta color** (#ff00ff)
- 🔍 **Larger node size** (30 vs 15-20)
- 💡 **Label**: "⭐ YOUR_IP (YOU)"
- ✨ **Pulsing glow effect**

**How It Works**:
1. Node writes IP to `output/node_info.json`
2. API server reads this file
3. Frontend fetches via `/api/node/info`
4. NetworkGraph component highlights matching node

**Mobile Device**: When IP changes, highlighting automatically updates after next topology refresh (30 seconds).

### Mobility Path Visualization
With `cleanup_old_location: false`, you can see your device's path:
- Each IP you've connected from appears as a node
- Connections between locations show routing paths
- Different subnets = different colors/regions

## Testing Mobility

### Simulate IP Change
For testing without actually moving:

**Method 1: Manual IP Change (if you have VPN)**
```bash
# Start node
python -m src.main

# Change VPN location
# Node will detect new IP after 60 seconds
```

**Method 2: Mock Testing**
Modify `_get_external_ip()` to return different IPs:
```python
# For testing only
def _get_external_ip(self):
    import random
    return f"203.0.113.{random.randint(1, 254)}"
```

### Expected Logs
```
INFO - External IP: 203.0.113.45
INFO - Added 254 IPs from own subnet 203.0.113.0/24
...
WARNING - 🚀 MOBILITY DETECTED: 203.0.113.45 -> 198.51.100.78
INFO - Device moved to new location/network - remapping subnet
INFO - 🔄 Handling mobility: 203.0.113.45 -> 198.51.100.78
INFO - Removed 254 old subnet targets from 203.0.113.0/24
INFO - Added 254 new subnet targets for 198.51.100.78/24
INFO - ✅ Mobility handling complete - now mapping from new location
INFO - Total mobility events: 1
```

## Edge Cases

### 1. Rapid IP Flapping
**Problem**: IP changes every few seconds (unstable connection)

**Handling**:
- Each change triggers remapping
- Old subnet removed, new subnet added
- Could cause high churn

**Mitigation**: Add debouncing - only remap if IP stable for N seconds

### 2. Same Subnet, Different IP
**Problem**: IP changes from `203.0.113.45` → `203.0.113.78` (same /24)

**Handling**:
- Mobility detected
- Removes old subnet targets
- Adds new subnet targets
- **Result**: Same 254 IPs re-added (minimal impact)

**Optimization**: Could check if subnet changed before remapping

### 3. Private IP ↔ Public IP
**Problem**: Device switches from private IP (behind NAT) to public IP (direct)

**Handling**:
- Only public IPs used for external communication
- NAT detection handles private IPs
- Mobility handling only affects public IP changes

### 4. Multiple Network Interfaces
**Problem**: Device has WiFi + Cellular, both active

**Handling**:
- Node uses single "external" IP (from NAT detection)
- If primary interface changes, mobility triggered
- Secondary interfaces ignored

## Comparison: Stationary vs Mobile

| Aspect | Stationary Node | Mobile Node |
|--------|----------------|-------------|
| **IP Changes** | Never | Frequent (minutes to hours) |
| **Subnet Mapping** | Single /24 | Multiple /24s over time |
| **Graph Coverage** | Local network | Wide geographic area |
| **Perspective** | Static location | Dynamic routing from many points |
| **Mobility Events** | 0 | Many (tracked in history) |
| **Historical Data** | Single location | Path of movement |
| **Network Contribution** | Deep local knowledge | Broad geographic coverage |

## Best Practices

### For Mobile Phone Users
```yaml
mobility:
  cleanup_old_location: true  # Don't keep every cell tower's data
  detect_interval: 30  # Check more frequently for tower switches
```

### For Satellite Operators
```yaml
mobility:
  cleanup_old_location: true  # Critical - prevents massive graph
  detect_interval: 120  # Less frequent (ground station changes known)
```

### For Laptop Users
```yaml
mobility:
  cleanup_old_location: false  # Keep history of coffee shops visited
  detect_interval: 60  # Default is fine
```

### For Stationary Servers
```yaml
mobility:
  cleanup_old_location: false  # N/A - won't move
  detect_interval: 300  # Can check less frequently to save resources
```

## Benefits of Mobile Node Support

### 1. Geographic Diversity
Mobile devices provide routing data from many locations that stationary nodes can't reach.

### 2. Temporal Perspective
Same device measuring same route from different locations shows routing changes over time/space.

### 3. Real-World Network Testing
Mobile nodes test how networks handle roaming devices - crucial for understanding modern internet infrastructure.

### 4. Coverage Expansion
Single mobile device can contribute as much data as dozens of stationary nodes by moving through different networks.

### 5. Unique Insights
Satellite nodes reveal ground station routing. Vehicle nodes show highway corridor connectivity. Mobile phones show cellular network topology.

## Troubleshooting

### "Mobility detection not working"
**Symptoms**: IP changed but no mobility logs

**Causes**:
- Heartbeat loop not running
- External IP detection failing
- Same subnet (false positive)

**Solution**: Check `_get_external_ip()` returns correct new IP

### "Too many mobility events"
**Symptoms**: IP changes every few seconds

**Causes**:
- Unstable connection
- VPN switching servers
- Load balancer rotating IPs

**Solution**: Increase `detect_interval` or add debouncing logic

### "Old subnet data not removed"
**Symptoms**: Still tracing old IPs after move

**Causes**:
- `_handle_mobility()` not completing
- Exception during cleanup
- trace_targets not updated

**Solution**: Check logs for errors in mobility handling

### "Visualizer shows wrong IP"
**Symptoms**: Magenta highlight on old IP

**Causes**:
- `node_info.json` not updated
- Frontend not refreshing
- API server caching

**Solution**: Restart frontend or wait 30s for auto-refresh

## Future Enhancements

### Planned
- [ ] **Debouncing**: Only remap if IP stable for N seconds
- [ ] **Smart subnet detection**: Don't remap if subnet unchanged
- [ ] **Mobility prediction**: Predict next IP based on history
- [ ] **Path visualization**: Show movement path on map

### Under Consideration
- [ ] **Geolocation**: Map IPs to geographic locations
- [ ] **Velocity calculation**: Speed of device movement
- [ ] **Network quality tracking**: Compare networks visited
- [ ] **Mobile-specific optimizations**: Battery-aware scanning

---

**Status**: ✅ Fully Implemented  
**Version**: 2.0  
**Last Updated**: 2024-10-24

