"""
Main node implementation for the distributed topology mapper
"""
import asyncio
import logging
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
from pathlib import Path
import json
import yaml
import sys
import requests

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ipfs.client import IPFSClient
from src.traceroute.tracer import Traceroute
from src.graph.gexf_generator import NetworkGraph, GEXFGenerator
from src.bandwidth.bandwidth_tester import IPerf3Client, SpeedtestClient
from src.nat_detection import detect_nat, test_connectivity

logger = logging.getLogger(__name__)


class PeerInfo:
    """Information about a discovered peer node."""
    
    def __init__(self, node_id: str, external_ip: str, last_seen: datetime):
        self.node_id = node_id
        self.external_ip = external_ip
        self.last_seen = last_seen
        self.traceroute_count = 0
        self.bandwidth_tested = False
    
    def is_stale(self, timeout_seconds: int = 300) -> bool:
        """Check if peer hasn't been seen recently."""
        return (datetime.now() - self.last_seen).total_seconds() > timeout_seconds


class IPReachability:
    """Track IP reachability across all nodes."""
    
    def __init__(self, ip: str, reachable_by: Set[str] = None, unreachable_by: Set[str] = None, last_verified: datetime = None):
        self.ip = ip
        self.reachable_by: Set[str] = reachable_by if reachable_by is not None else set()
        self.unreachable_by: Set[str] = unreachable_by if unreachable_by is not None else set()
        self.last_verified = last_verified if last_verified is not None else datetime.now()
        self.verification_pending = False


class TopologyNode:
    """
    A participant node in the distributed topology mapping network.
    
    This node:
    - Discovers other nodes via IPFS PubSub
    - Performs traceroutes to other participant nodes
    - Automatically maps own subnet for comprehensive coverage
    - Collaboratively verifies IP reachability
    - Tests bandwidth to peers
    - Publishes topology data to IPFS
    - Maintains its own identity and status
    """
    
    def __init__(self, config_path: Optional[str] = None, node_id: Optional[str] = None):
        """
        Initialize a topology mapping node.
        
        Args:
            config_path: Path to configuration file
            node_id: Unique identifier for this node. If None, generates or loads one.
        """
        self.config = self._load_config(config_path)
        self.node_id = node_id or self._get_or_create_node_id()
        self.external_ip: Optional[str] = None
        self.peer_nodes: Dict[str, PeerInfo] = {}
        self.traceroute_results: Dict = {}
        self.running = False
        
        # IP reachability tracking
        self.ip_reachability: Dict[str, IPReachability] = {}
        
        # Targets to trace (includes peers, own subnet, and verification requests)
        self.trace_targets: Set[str] = set()
        
        # Components
        self.ipfs_client: Optional[IPFSClient] = None
        self.tracer: Optional[Traceroute] = None
        self.network_graph = NetworkGraph()
        
        # Background tasks
        self.tasks: List[asyncio.Task] = []
        
        logger.info(f"Initialized node {self.node_id}")
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from YAML file."""
        if not config_path:
            config_path = Path(__file__).parent.parent.parent / "config" / "default.yaml"
        
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load config: {e}, using defaults")
            return {
                "node": {
                    "traceroute": {"max_hops": 30, "timeout": 5, "interval": 3600},
                    "rate_limit": {"max_traceroutes_per_hour": 10}
                },
                "bandwidth": {
                    "enabled": True,
                    "iperf3": {"interval": 7200},
                    "speedtest": {"interval": 14400}
                },
                "ipfs": {"api_address": "/ip4/127.0.0.1/tcp/5001"}
            }
    
    def _get_or_create_node_id(self) -> str:
        """Get existing node ID or create a new one."""
        node_id_file = Path.home() / ".intermap" / "node_id"
        
        try:
            node_id_file.parent.mkdir(parents=True, exist_ok=True)
            
            if node_id_file.exists():
                node_id = node_id_file.read_text().strip()
                logger.info(f"Loaded existing node ID: {node_id}")
                return node_id
            else:
                import uuid
                node_id = f"node-{uuid.uuid4().hex[:12]}"
                node_id_file.write_text(node_id)
                logger.info(f"Created new node ID: {node_id}")
                return node_id
                
        except Exception as e:
            logger.warning(f"Failed to persist node ID: {e}")
            import uuid
            return f"node-{uuid.uuid4().hex[:12]}"
    
    def _get_external_ip(self) -> Optional[str]:
        """Detect external IP address."""
        try:
            # Try multiple services for reliability
            services = [
                "https://api.ipify.org",
                "https://ifconfig.me/ip",
                "https://icanhazip.com"
            ]
            
            for service in services:
                try:
                    response = requests.get(service, timeout=5)
                    if response.status_code == 200:
                        ip = response.text.strip()
                        logger.info(f"Detected external IP: {ip}")
                        return ip
                except:
                    continue
            
            logger.warning("Failed to detect external IP from all services")
            return None
            
        except Exception as e:
            logger.error(f"Error detecting external IP: {e}")
            return None
    
    async def start(self):
        """Start the node and begin participating in the network."""
        logger.info(f"Starting node {self.node_id}")
        self.running = True
        
        try:
            # Run connectivity tests
            logger.info("Running network connectivity tests...")
            connectivity = test_connectivity()
            
            if not connectivity["internet"]:
                logger.error("No internet connectivity detected!")
                return
            
            if not connectivity["traceroute"]:
                logger.warning("Traceroute not working - may need elevated privileges")
                logger.info("Try running with: sudo python launch.py (Linux/Mac) or as Administrator (Windows)")
            
            # Detect NAT
            is_nat, local_ip, external_ip = detect_nat()
            self.external_ip = external_ip
            
            if not self.external_ip:
                logger.error("Could not detect external IP - node may not be discoverable")
                return
            
            if is_nat:
                logger.info(f"Behind NAT: Local {local_ip} -> External {external_ip}")
            else:
                logger.info(f"Direct connection: {external_ip}")
            
            # Connect to IPFS
            ipfs_config = self.config.get("ipfs", {})
            self.ipfs_client = IPFSClient(ipfs_config.get("api_address", "/ip4/127.0.0.1/tcp/5001"))
            await self.ipfs_client.connect()
            
            # Initialize traceroute
            tracer_config = self.config.get("node", {}).get("traceroute", {})
            self.tracer = Traceroute(
                max_hops=tracer_config.get("max_hops", 30),
                timeout=tracer_config.get("timeout", 5),
                filter_private=True
            )
            
            # Announce presence to IPFS network (fully P2P, no central server)
            await self._announce_presence()
            
            # Add own subnet to trace targets if enabled
            if tracer_config.get("auto_map_own_subnet", True):
                await self._add_own_subnet_targets()
            
            # Start background tasks
            self.tasks.append(asyncio.create_task(self._heartbeat_loop()))
            self.tasks.append(asyncio.create_task(self._traceroute_loop()))
            self.tasks.append(asyncio.create_task(self._peer_cleanup_loop()))
            self.tasks.append(asyncio.create_task(self._ip_verification_loop()))
            
            if self.config.get("bandwidth", {}).get("enabled", True):
                self.tasks.append(asyncio.create_task(self._bandwidth_test_loop()))
            
            logger.info(f"Node {self.node_id} started successfully")
            logger.info(f"External IP: {self.external_ip}")
            logger.info(f"🌐 Fully decentralized P2P - discovering peers via IPFS DHT...")
            
        except Exception as e:
            logger.error(f"Failed to start node: {e}", exc_info=True)
            await self.stop()
            raise
    
    async def stop(self):
        """Stop the node and cleanup resources."""
        logger.info(f"Stopping node {self.node_id}")
        self.running = False
        
        # Cancel all background tasks
        for task in self.tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self.tasks.clear()
        
        # Disconnect from IPFS
        if self.ipfs_client:
            try:
                await self.ipfs_client.disconnect()
            except:
                pass
        
        logger.info(f"Node {self.node_id} stopped")
    
    async def _add_own_subnet_targets(self):
        """Add all IPs in own subnet to trace targets (configurable subnet size)."""
        if not self.external_ip:
            return
        
        try:
            import ipaddress
            
            # Get subnet size from config (default /24)
            subnet_size = self.config.get("node", {}).get("traceroute", {}).get("subnet_size", 24)
            
            # Validate subnet size (must be between 8 and 30)
            if subnet_size < 8 or subnet_size > 30:
                logger.error(f"Invalid subnet_size {subnet_size}. Must be between 8 and 30. Using default /24.")
                subnet_size = 24
            
            # Calculate network
            ip_obj = ipaddress.ip_address(self.external_ip)
            network = ipaddress.ip_network(f"{self.external_ip}/{subnet_size}", strict=False)
            
            # Count total IPs (for large subnets, this could be millions)
            total_ips = network.num_addresses - 2  # Exclude network and broadcast
            
            # Warn if subnet is very large
            if subnet_size < 16:
                logger.warning(f"⚠️ Large subnet /{subnet_size} will map {total_ips:,} IPs!")
                logger.warning(f"This will take significant time and resources.")
                logger.warning(f"Consider using a larger prefix (e.g., /20 or /24) for manageable scope.")
            
            # Add all IPs in subnet to trace targets
            count = 0
            max_ips = 100000  # Safety limit to prevent memory issues
            
            for ip in network.hosts():
                ip_str = str(ip)
                if ip_str != self.external_ip:  # Don't trace to self
                    self.trace_targets.add(ip_str)
                    count += 1
                    
                    # Safety check for very large subnets
                    if count >= max_ips:
                        logger.warning(f"⚠️ Reached safety limit of {max_ips:,} IPs. Stopping subnet enumeration.")
                        logger.warning(f"Use a larger subnet prefix to reduce scope (e.g., /{subnet_size+4})")
                        break
            
            logger.info(f"Added {count:,} IPs from own subnet {network} (/{subnet_size}) to trace targets")
            logger.info(f"This provides comprehensive mapping from your network perspective")
            
            if subnet_size <= 20:
                logger.info(f"💡 TIP: For faster mapping, consider reducing subnet size in config (e.g., /24 or /28)")
            
        except Exception as e:
            logger.error(f"Failed to add own subnet targets: {e}")
    
    async def _handle_mobility(self, old_ip: str, new_ip: str):
        """
        Handle device mobility when external IP changes.
        
        This is critical for:
        - Mobile phones (switching cell towers, WiFi networks)
        - Satellites (changing ground stations as they orbit)
        - Laptops (moving between locations/networks)
        - Any WiFi/5G enabled portable devices
        
        Args:
            old_ip: Previous external IP
            new_ip: New external IP
        """
        try:
            logger.info(f"🔄 Handling mobility: {old_ip} -> {new_ip}")
            
            # Get subnet size from config
            subnet_size = self.config.get("node", {}).get("traceroute", {}).get("subnet_size", 24)
            
            # 1. Remove old subnet targets
            import ipaddress
            if old_ip:
                old_network = ipaddress.ip_network(f"{old_ip}/{subnet_size}", strict=False)
                old_targets = {str(ip) for ip in old_network.hosts()}
                removed_count = 0
                for target in old_targets:
                    if target in self.trace_targets:
                        self.trace_targets.discard(target)
                        removed_count += 1
                logger.info(f"Removed {removed_count:,} old subnet targets from {old_network}")
            
            # 2. Add new subnet targets
            if self.config.get("node", {}).get("traceroute", {}).get("auto_map_own_subnet", True):
                await self._add_own_subnet_targets()
                logger.info(f"Added new subnet targets for {new_ip}/{subnet_size}")
            
            # 3. Mark node as mobile in graph metadata
            if not hasattr(self, 'mobility_events'):
                self.mobility_events = []
            
            from datetime import datetime
            self.mobility_events.append({
                "timestamp": datetime.now().isoformat(),
                "old_ip": old_ip,
                "new_ip": new_ip,
                "reason": "ip_change_detected"
            })
            
            # Keep only last 10 mobility events to prevent memory bloat
            if len(self.mobility_events) > 10:
                self.mobility_events = self.mobility_events[-10:]
            
            # 4. Optionally clean up old location data from graph
            # (Keep it for now to show path history - could be disabled with config)
            cleanup_old = self.config.get("node", {}).get("mobility", {}).get("cleanup_old_location", False)
            if cleanup_old:
                # Remove nodes from old subnet that we mapped
                old_subnet_nodes = [ip for ip in self.network_graph.nodes.keys() 
                                   if ip.startswith('.'.join(old_ip.split('.')[0:3]))]
                for node_ip in old_subnet_nodes:
                    self.network_graph.remove_node(node_ip)
                logger.info(f"Cleaned up {len(old_subnet_nodes)} nodes from old location")
            
            logger.info(f"✅ Mobility handling complete - now mapping from new location")
            logger.info(f"Total mobility events: {len(self.mobility_events)}")
            
        except Exception as e:
            logger.error(f"Error handling mobility: {e}")
    
    async def _announce_presence(self):
        """Announce node presence to IPFS network using DHT (fully P2P)."""
        try:
            cid = await self.ipfs_client.announce_node(
                self.node_id,
                self.external_ip,
                api_port=5000
            )
            
            if cid:
                logger.info(f"✓ Node announced to IPFS network: {cid}")
                logger.info(f"  Node ID: {self.node_id}")
                logger.info(f"  External IP: {self.external_ip}")
                logger.info("  Fully P2P - No central server required!")
            else:
                logger.debug("IPFS not available for node announcement")
                
        except Exception as e:
            logger.debug(f"Could not announce presence: {e}")
    
    async def _heartbeat_loop(self):
        """Periodically announce presence and discover peers via IPFS DHT (P2P)."""
        while self.running:
            try:
                await asyncio.sleep(60)  # Heartbeat every 60 seconds
                
                # Check if external IP changed (mobile devices, satellites, laptops)
                new_ip = self._get_external_ip()
                if new_ip and new_ip != self.external_ip:
                    logger.warning(f"🚀 MOBILITY DETECTED: External IP changed: {self.external_ip} -> {new_ip}")
                    logger.info(f"Device moved to new location/network - remapping subnet")
                    
                    old_ip = self.external_ip
                    self.external_ip = new_ip
                    
                    # Handle mobile device relocation
                    await self._handle_mobility(old_ip, new_ip)
                
                # Re-announce presence to IPFS network
                await self._announce_presence()
                
                # Discover peers through IPFS DHT
                peers = await self.ipfs_client.discover_peers()
                if peers:
                    logger.info(f"Discovered {len(peers)} peers via IPFS DHT")
                    for peer_info in peers:
                        node_id = peer_info.get("node_id")
                        if node_id and node_id != self.node_id and node_id not in self.peer_nodes:
                            logger.info(f"New peer discovered: {node_id} @ {peer_info.get('external_ip')}")
                            self.peer_nodes[node_id] = PeerInfo(
                                node_id=node_id,
                                external_ip=peer_info.get("external_ip"),
                                last_seen=datetime.now()
                            )
                
                logger.debug(f"Heartbeat: {len(self.peer_nodes)} known peers, fully P2P via IPFS")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
    
    async def _handle_discovery_message(self, message: Dict):
        """Handle discovery channel messages."""
        try:
            msg_type = message.get("type")
            node_id = message.get("node_id")
            
            # Ignore our own messages
            if node_id == self.node_id:
                return
            
            if msg_type == "presence":
                external_ip = message.get("external_ip")
                
                if node_id not in self.peer_nodes:
                    logger.info(f"Discovered new peer: {node_id} @ {external_ip}")
                
                # Update or add peer
                self.peer_nodes[node_id] = PeerInfo(
                    node_id=node_id,
                    external_ip=external_ip,
                    last_seen=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"Error handling discovery message: {e}")
    
    async def _handle_topology_message(self, message: Dict):
        """Handle topology channel messages."""
        try:
            msg_type = message.get("type")
            
            if msg_type == "topology_update":
                cid = message.get("cid")
                node_id = message.get("node_id")
                
                logger.info(f"Received topology update from {node_id}: {cid}")
                # TODO: Download and merge topology data
                
        except Exception as e:
            logger.error(f"Error handling topology message: {e}")
    
    async def _handle_verification_message(self, message: Dict):
        """Handle verification channel messages for collaborative dead IP detection."""
        try:
            msg_type = message.get("type")
            
            if msg_type == "verification_request":
                ip = message.get("ip")
                requesting_node = message.get("requesting_node")
                
                # Ignore our own requests
                if requesting_node == self.node_id:
                    return
                
                logger.info(f"Received verification request for {ip} from {requesting_node}")
                
                # Immediately attempt traceroute
                try:
                    hops = self.tracer.trace(ip)
                    reachable = bool(hops)
                    
                    # Send back result
                    response_msg = {
                        "type": "verification_response",
                        "ip": ip,
                        "responding_node": self.node_id,
                        "reachable": reachable,
                        "hop_count": len(hops) if hops else 0,
                        "timestamp": datetime.now().isoformat()
                    }
                    await self.ipfs_client.publish(IPFSClient.VERIFICATION_CHANNEL, response_msg)
                    
                    # Update local tracking
                    if ip in self.ip_reachability:
                        if reachable:
                            self.ip_reachability[ip].reachable_by.add(self.node_id)
                            self.ip_reachability[ip].unreachable_by.discard(self.node_id)
                        else:
                            self.ip_reachability[ip].unreachable_by.add(self.node_id)
                            self.ip_reachability[ip].reachable_by.discard(self.node_id)
                        self.ip_reachability[ip].last_verified = datetime.now()
                    else:
                        self.ip_reachability[ip] = IPReachability(
                            ip=ip,
                            reachable_by={self.node_id} if reachable else set(),
                            unreachable_by=set() if reachable else {self.node_id},
                            last_verified=datetime.now()
                        )
                    
                    logger.info(f"Verification complete for {ip}: {'reachable' if reachable else 'unreachable'}")
                    
                except Exception as e:
                    logger.error(f"Error verifying {ip}: {e}")
            
            elif msg_type == "verification_response":
                ip = message.get("ip")
                responding_node = message.get("responding_node")
                reachable = message.get("reachable")
                
                logger.info(f"Received verification response from {responding_node}: {ip} is {'reachable' if reachable else 'unreachable'}")
                
                # Update tracking
                if ip in self.ip_reachability:
                    if reachable:
                        self.ip_reachability[ip].reachable_by.add(responding_node)
                        self.ip_reachability[ip].unreachable_by.discard(responding_node)
                    else:
                        self.ip_reachability[ip].unreachable_by.add(responding_node)
                        self.ip_reachability[ip].reachable_by.discard(responding_node)
                    self.ip_reachability[ip].last_verified = datetime.now()
                else:
                    self.ip_reachability[ip] = IPReachability(
                        ip=ip,
                        reachable_by={responding_node} if reachable else set(),
                        unreachable_by=set() if reachable else {responding_node},
                        last_verified=datetime.now()
                    )
        
        except Exception as e:
            logger.error(f"Error handling verification message: {e}")
    
    async def _ip_verification_loop(self):
        """Monitor IP reachability and remove dead IPs from map."""
        while self.running:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                # Calculate threshold: 5% of total nodes (peers + self)
                total_nodes = len(self.peer_nodes) + 1  # +1 for self
                threshold = max(1, int(total_nodes * 0.05))  # At least 1 node
                
                logger.debug(f"IP verification: {total_nodes} total nodes, threshold={threshold} (5%)")
                
                # Find IPs that need to be removed (no node can reach them)
                ips_to_remove = []
                
                for ip, reachability in self.ip_reachability.items():
                    # Skip if verification is still pending
                    if reachability.verification_pending:
                        # Check if verification has timed out (10 minutes)
                        if (datetime.now() - reachability.last_verified).total_seconds() > 600:
                            reachability.verification_pending = False
                        else:
                            continue
                    
                    # If no nodes can reach it and at least 5% of nodes have tried
                    if (not reachability.reachable_by and 
                        len(reachability.unreachable_by) >= threshold):
                        ips_to_remove.append(ip)
                        logger.warning(f"IP {ip} is unreachable by {len(reachability.unreachable_by)} nodes (threshold: {threshold}) - marking for removal")
                
                # Remove dead IPs from graph
                for ip in ips_to_remove:
                    if ip in self.network_graph.nodes:
                        logger.info(f"Removing dead IP {ip} from network graph")
                        self.network_graph.remove_node(ip)
                    
                    # Clean up tracking
                    del self.ip_reachability[ip]
                    self.trace_targets.discard(ip)
                
                if ips_to_remove:
                    logger.info(f"Removed {len(ips_to_remove)} dead IPs from map")
                    # Publish updated topology
                    await self._publish_topology()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in IP verification loop: {e}")
                await asyncio.sleep(60)

    
    async def _peer_cleanup_loop(self):
        """Remove stale peers that haven't sent heartbeat."""
        while self.running:
            try:
                await asyncio.sleep(120)  # Check every 2 minutes
                
                stale_peers = [
                    node_id for node_id, peer in self.peer_nodes.items()
                    if peer.is_stale(timeout_seconds=300)  # 5 minutes
                ]
                
                for node_id in stale_peers:
                    logger.info(f"Removing stale peer: {node_id}")
                    del self.peer_nodes[node_id]
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in peer cleanup loop: {e}")
    
    async def _traceroute_loop(self):
        """Continuously perform traceroutes to all targets (peers + subnet + verifications)."""
        interval = self.config.get("node", {}).get("traceroute", {}).get("interval", 300)
        
        while self.running:
            try:
                # Combine all targets: peers + subnet IPs + any verification targets
                all_targets = set()
                
                # Add peer IPs
                for peer in self.peer_nodes.values():
                    all_targets.add(peer.external_ip)
                
                # Add subnet targets
                all_targets.update(self.trace_targets)
                
                if not all_targets:
                    logger.info("No targets to trace yet, waiting...")
                    await asyncio.sleep(30)
                    continue
                
                logger.info(f"Starting traceroute cycle for {len(all_targets)} targets")
                
                for target_ip in all_targets:
                    if not self.running:
                        break
                    
                    try:
                        logger.info(f"Tracing route to: {target_ip}")
                        
                        # Perform traceroute (no hop limit, no rate limit)
                        hops = self.tracer.trace(target_ip)
                        
                        if hops:
                            # Add to graph
                            for i, hop in enumerate(hops):
                                self.network_graph.add_node(hop.ip_address, hop.hostname)
                                
                                # Add edge between consecutive hops
                                if i > 0:
                                    prev_hop = hops[i-1]
                                    rtt_diff = abs(hop.rtt_ms - prev_hop.rtt_ms)
                                    self.network_graph.add_edge(
                                        prev_hop.ip_address,
                                        hop.ip_address,
                                        rtt_ms=rtt_diff
                                    )
                            
                            # Mark as reachable
                            if target_ip in self.ip_reachability:
                                self.ip_reachability[target_ip].reachable_by.add(self.node_id)
                                self.ip_reachability[target_ip].unreachable_by.discard(self.node_id)
                                self.ip_reachability[target_ip].last_verified = datetime.now()
                            else:
                                self.ip_reachability[target_ip] = IPReachability(
                                    ip=target_ip,
                                    reachable_by={self.node_id},
                                    unreachable_by=set(),
                                    last_verified=datetime.now()
                                )
                            
                            logger.info(f"Traceroute complete: {len(hops)} hops to {target_ip}")
                        else:
                            # Traceroute failed - flag for verification
                            logger.warning(f"Traceroute failed to {target_ip}")
                            
                            # Mark as unreachable
                            if target_ip in self.ip_reachability:
                                self.ip_reachability[target_ip].unreachable_by.add(self.node_id)
                                self.ip_reachability[target_ip].reachable_by.discard(self.node_id)
                                self.ip_reachability[target_ip].last_verified = datetime.now()
                            else:
                                self.ip_reachability[target_ip] = IPReachability(
                                    ip=target_ip,
                                    reachable_by=set(),
                                    unreachable_by={self.node_id},
                                    last_verified=datetime.now()
                                )
                            
                            # If IP is in graph, request verification from all nodes
                            if target_ip in self.network_graph.nodes:
                                logger.warning(f"IP {target_ip} is in graph but unreachable - requesting verification")
                                self.ip_reachability[target_ip].verification_pending = True
                                
                                # Broadcast verification request
                                verification_msg = {
                                    "type": "verification_request",
                                    "ip": target_ip,
                                    "requesting_node": self.node_id,
                                    "timestamp": datetime.now().isoformat()
                                }
                                await self.ipfs_client.publish(IPFSClient.VERIFICATION_CHANNEL, verification_msg)
                        
                        # Delay between traces
                        await asyncio.sleep(10)
                        
                    except Exception as e:
                        logger.error(f"Error tracing to {target_ip}: {e}")
                
                # Publish updated topology
                await self._publish_topology()
                
                # Wait before next round
                logger.info(f"Traceroute round complete. Waiting {interval}s for next round...")
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in traceroute loop: {e}")
                await asyncio.sleep(60)
    
    async def _bandwidth_test_loop(self):
        """Periodically test bandwidth to peers and public servers."""
        iperf3_interval = self.config.get("bandwidth", {}).get("iperf3", {}).get("interval", 7200)
        speedtest_interval = self.config.get("bandwidth", {}).get("speedtest", {}).get("interval", 14400)
        
        last_iperf3 = datetime.now() - timedelta(seconds=iperf3_interval)
        last_speedtest = datetime.now() - timedelta(seconds=speedtest_interval)
        
        iperf3_client = IPerf3Client()
        speedtest_client = SpeedtestClient()
        
        while self.running:
            try:
                now = datetime.now()
                
                # iperf3 tests to public servers
                if (now - last_iperf3).total_seconds() >= iperf3_interval:
                    logger.info("Running iperf3 bandwidth tests...")
                    
                    for server_config in self.config.get("bandwidth", {}).get("public_servers", []):
                        if not self.running:
                            break
                        
                        try:
                            server = server_config.get("host")
                            port = server_config.get("port", 5201)
                            
                            result = iperf3_client.test_bandwidth(server, port)
                            if result:
                                logger.info(f"iperf3 to {server}: {result.download_mbps:.2f} Mbps down, {result.upload_mbps:.2f} Mbps up")
                                
                                # Update graph edges with bandwidth
                                # Find edges to this server and update
                                if server in self.network_graph.nodes:
                                    for edge in self.network_graph.edges.values():
                                        if edge.target == server:
                                            edge.bandwidth_mbps = result.download_mbps
                            
                        except Exception as e:
                            logger.error(f"iperf3 test failed to {server}: {e}")
                    
                    last_iperf3 = now
                
                # Speedtest to internet
                if (now - last_speedtest).total_seconds() >= speedtest_interval:
                    logger.info("Running speedtest...")
                    
                    try:
                        result = speedtest_client.test_bandwidth()
                        if result:
                            logger.info(f"Speedtest: {result.download_mbps:.2f} Mbps down, {result.upload_mbps:.2f} Mbps up, {result.latency_ms:.2f}ms latency")
                    except Exception as e:
                        logger.error(f"Speedtest failed: {e}")
                    
                    last_speedtest = now
                
                # Wait before checking again
                await asyncio.sleep(60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in bandwidth test loop: {e}")
                await asyncio.sleep(60)
    
    async def _publish_topology(self):
        """Generate GEXF and publish to IPFS."""
        try:
            # Generate GEXF file
            output_dir = Path(__file__).parent.parent.parent / "output"
            output_dir.mkdir(exist_ok=True)
            
            # Write node info for API server (for visualizer highlighting)
            node_info_path = output_dir / "node_info.json"
            import json
            with open(node_info_path, 'w') as f:
                json.dump({
                    "external_ip": self.external_ip,
                    "node_id": self.node_id,
                    "timestamp": datetime.now().isoformat(),
                    "mobility_events": getattr(self, 'mobility_events', [])
                }, f, indent=2)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            gexf_path = output_dir / f"topology_{self.node_id}_{timestamp}.gexf"
            
            generator = GEXFGenerator(self.network_graph)
            generator.save_to_file(str(gexf_path))
            
            logger.info(f"Generated GEXF: {gexf_path}")
            
            # Publish to IPFS network (fully P2P, no central server)
            try:
                cid = await self.ipfs_client.publish_topology(str(gexf_path))
                
                if cid:
                    logger.info(f"✓ Topology published to IPFS: {cid}")
                    logger.info(f"  Nodes: {len(self.network_graph.nodes)}, Edges: {len(self.network_graph.edges)}")
                    logger.info("  Other nodes can fetch topology directly from IPFS!")
                else:
                    logger.info("Topology saved locally - IPFS publishing skipped")
                
            except Exception as pub_error:
                logger.debug(f"Could not publish to IPFS: {pub_error}")
                logger.info("Topology saved locally - visualizer will use local file")
            
        except Exception as e:
            logger.error(f"Failed to generate topology: {e}")


if __name__ == "__main__":
    # Basic testing
    logging.basicConfig(level=logging.INFO)
    
    async def test():
        node = TopologyNode()
        await node.start()
        
        # Run for a while
        await asyncio.sleep(300)
        
        await node.stop()
    
    asyncio.run(test())
