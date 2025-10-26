"""
Intermap - Distributed P2P Internet Topology Mapper
Copyright (c) 2025 Jay Wenden
Licensed under CC-BY-NC-SA 4.0
"""
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
from src.traceroute.tracer import Traceroute, detect_local_subnet, get_live_subnet_hosts
from src.graph.gexf_generator import NetworkGraph, GEXFGenerator
from src.bandwidth.bandwidth_tester import IPerf3Client, SpeedtestClient, BandwidthTestManager
from src.nat_detection import detect_nat, test_connectivity
from src.utils import is_private_ip

logger = logging.getLogger(__name__)

# Import iperf3 server fetcher (after logger defined)
try:
    from src.iperf3_servers import fetch_iperf3_servers
    IPERF3_FETCHER_AVAILABLE = True
except ImportError as e:
    IPERF3_FETCHER_AVAILABLE = False
    fetch_iperf3_servers = None
    logger.warning(f"iperf3 fetcher import failed: {e}")

logger = logging.getLogger(__name__)


class PeerInfo:
    """Information about a discovered peer node."""
    
    def __init__(self, node_id: str, external_ip: str, last_seen: datetime, iperf3_port: int = 5201):
        self.node_id = node_id
        self.external_ip = external_ip
        self.last_seen = last_seen
        self.iperf3_port = iperf3_port
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
        
        # Two separate graphs for privacy
        self.local_graph = NetworkGraph()  # Full topology including private IPs (for own visualization)
        self.network_graph = NetworkGraph()  # Only public IPs (for IPFS sharing)
        
        self.bandwidth_manager: Optional[BandwidthTestManager] = None
        
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
                filter_private=True,
                verify_reachable=tracer_config.get("verify_reachable", True)
            )
            
            # Initialize bandwidth manager
            bandwidth_config = self.config.get("bandwidth", {}).get("iperf3", {})
            self.bandwidth_manager = BandwidthTestManager(
                duration=bandwidth_config.get("duration", 10)
            )
            
            # Add well-known targets from config (resolve hostnames to IPs)
            well_known = self.config.get("node", {}).get("well_known_targets", [])
            if well_known:
                logger.info(f"Adding {len(well_known)} well-known targets from config")
                resolved_config_targets = []
                for target in well_known:
                    # Try to parse as IP first
                    try:
                        import ipaddress
                        ipaddress.ip_address(target)
                        # It's a valid IP, add it directly
                        resolved_config_targets.append(target)
                        logger.debug(f"Config target is IP: {target}")
                    except ValueError:
                        # Not a valid IP, must be a hostname - resolve it
                        try:
                            from src.iperf3_servers import resolve_hostname
                            resolved_ip = resolve_hostname(target, timeout=2)
                            if resolved_ip:
                                resolved_config_targets.append(resolved_ip)
                                logger.info(f"✓ Resolved {target} -> {resolved_ip}")
                            else:
                                logger.warning(f"Could not resolve config target: {target}")
                        except Exception as e:
                            logger.warning(f"Failed to resolve config target {target}: {e}")
                
                if resolved_config_targets:
                    logger.info(f"✓ Added {len(resolved_config_targets)}/{len(well_known)} config targets")
                    self.trace_targets.update(resolved_config_targets)
            
            # Fetch ALL iperf3 servers dynamically from GitHub
            if IPERF3_FETCHER_AVAILABLE and fetch_iperf3_servers:
                try:
                    logger.info("Fetching ALL iperf3 servers from GitHub repository...")
                    iperf3_servers = fetch_iperf3_servers(timeout=10)
                    
                    if iperf3_servers:
                        # Extract unique hosts
                        iperf3_hosts = list(set([s['host'] for s in iperf3_servers]))
                        logger.info(f"✓ Fetched {len(iperf3_hosts)} unique iperf3 server hosts from GitHub")
                        self.trace_targets.update(iperf3_hosts)
                        
                        # Log sample
                        if iperf3_hosts:
                            logger.info(f"Sample servers: {', '.join(iperf3_hosts[:5])}")
                    else:
                        logger.warning("No iperf3 servers fetched - using config only")
                        
                except Exception as e:
                    logger.error(f"Failed to fetch iperf3 servers from GitHub: {e}")
                    logger.info("Continuing with config targets only")
            else:
                logger.warning("iperf3 fetcher not available - using config targets only")
            
            logger.info(f"Total trace targets loaded: {len(self.trace_targets)}")
            if self.trace_targets:
                logger.info(f"First 10 targets: {list(self.trace_targets)[:10]}")
            
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
            self.tasks.append(asyncio.create_task(self._map_verification_loop()))  # New: verify all IPs in map
            
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
        """Detect subnet and add only LIVE hosts to trace targets (using ping sweep)."""
        if not self.external_ip:
            return
        
        try:
            logger.info("Detecting local subnet and finding live hosts...")
            
            # Use new subnet detection and ping sweep
            live_hosts = get_live_subnet_hosts(max_hosts=254)
            
            if live_hosts:
                # Add live hosts to trace targets AND to the graph
                # ANY IP that responds to ping goes in the map
                for ip in live_hosts:
                    # Add to local graph (includes private IPs)
                    self.local_graph.add_node(ip, hostname=ip)
                    
                    # Add to network graph only if public
                    if not is_private_ip(ip):
                        self.network_graph.add_node(ip, hostname=ip)
                    
                    if ip != self.external_ip:  # Don't trace to self
                        self.trace_targets.add(ip)
                
                logger.info(f"✅ Added {len(live_hosts)} live hosts from local subnet to map and trace targets")
            else:
                logger.warning("No live hosts found in local subnet")
            
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
                # Remove nodes from old subnet that we mapped (from both graphs)
                old_subnet_prefix = '.'.join(old_ip.split('.')[0:3])
                old_subnet_nodes = [ip for ip in self.local_graph.nodes.keys() 
                                   if ip.startswith(old_subnet_prefix)]
                for node_ip in old_subnet_nodes:
                    self.local_graph.remove_node(node_ip)
                    if node_ip in self.network_graph.nodes:
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
                api_port=5000,
                iperf3_port=5201  # Announce iperf3 capability
            )
            
            if cid:
                logger.info(f"✓ Node announced to IPFS network: {cid}")
                logger.info(f"  Node ID: {self.node_id}")
                logger.info(f"  External IP: {self.external_ip}")
                logger.info(f"  iperf3: Port 5201")
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
            protocol_version = message.get("protocol_version")
            
            # Ignore our own messages
            if node_id == self.node_id:
                return
            
            # Verify it's actually an Intermap node
            if protocol_version != "intermap-v1":
                logger.debug(f"Ignoring non-Intermap message from {node_id}")
                return
            
            # Handle node announcements (new discovery method)
            if msg_type == "node_announcement":
                external_ip = message.get("external_ip")
                iperf3_port = message.get("iperf3_port", 5201)
                
                if node_id not in self.peer_nodes:
                    logger.info(f"✓ Discovered Intermap node: {node_id} @ {external_ip} (iperf3:{iperf3_port})")
                
                # Update or add peer
                self.peer_nodes[node_id] = PeerInfo(
                    node_id=node_id,
                    external_ip=external_ip,
                    last_seen=datetime.now(),
                    iperf3_port=iperf3_port
                )
            
            # Legacy presence messages (for backward compatibility)
            elif msg_type == "presence":
                external_ip = message.get("external_ip")
                iperf3_port = message.get("iperf3_port", 5201)
                
                if node_id not in self.peer_nodes:
                    logger.info(f"Discovered new peer: {node_id} @ {external_ip} (iperf3:{iperf3_port})")
                
                # Update or add peer
                self.peer_nodes[node_id] = PeerInfo(
                    node_id=node_id,
                    external_ip=external_ip,
                    last_seen=datetime.now(),
                    iperf3_port=iperf3_port
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
                    # Remove from both graphs
                    if ip in self.local_graph.nodes:
                        logger.info(f"Removing dead IP {ip} from graphs")
                        self.local_graph.remove_node(ip)
                    if ip in self.network_graph.nodes:
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

    async def _map_verification_loop(self):
        """
        Continuously verify ALL IPs in the map are still online.
        Ping every IP periodically and request cross-node verification if down.
        """
        while self.running:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                # Get all IPs currently in the map (use local_graph which has all IPs)
                all_ips = list(self.local_graph.nodes.keys())
                
                if not all_ips:
                    logger.debug("No IPs in map yet")
                    continue
                
                logger.info(f"Verifying {len(all_ips)} IPs in map...")
                
                # Ping all IPs to verify they're still online
                import platform
                import subprocess
                
                online_count = 0
                offline_count = 0
                
                for ip in all_ips:
                    try:
                        # Quick ping test
                        if platform.system() == "Windows":
                            cmd = ["ping", "-n", "1", "-w", "1000", ip]
                        else:
                            cmd = ["ping", "-c", "1", "-W", "1", ip]
                        
                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            timeout=2
                        )
                        
                        if result.returncode == 0:
                            # Still online
                            online_count += 1
                            
                            # Update reachability
                            if ip in self.ip_reachability:
                                self.ip_reachability[ip].reachable_by.add(self.node_id)
                                self.ip_reachability[ip].unreachable_by.discard(self.node_id)
                                self.ip_reachability[ip].last_verified = datetime.now()
                            else:
                                self.ip_reachability[ip] = IPReachability(
                                    ip=ip,
                                    reachable_by={self.node_id},
                                    unreachable_by=set(),
                                    last_verified=datetime.now()
                                )
                        else:
                            # Appears offline - request verification from other nodes
                            offline_count += 1
                            logger.warning(f"IP {ip} appears offline - requesting verification")
                            
                            # Update reachability
                            if ip in self.ip_reachability:
                                self.ip_reachability[ip].unreachable_by.add(self.node_id)
                                self.ip_reachability[ip].reachable_by.discard(self.node_id)
                                self.ip_reachability[ip].last_verified = datetime.now()
                                self.ip_reachability[ip].verification_pending = True
                            else:
                                self.ip_reachability[ip] = IPReachability(
                                    ip=ip,
                                    reachable_by=set(),
                                    unreachable_by={self.node_id},
                                    last_verified=datetime.now()
                                )
                                self.ip_reachability[ip].verification_pending = True
                            
                            # Request verification from other nodes
                            verification_msg = {
                                "type": "verification_request",
                                "ip": ip,
                                "requesting_node": self.node_id,
                                "timestamp": datetime.now().isoformat()
                            }
                            await self.ipfs_client.publish(IPFSClient.VERIFICATION_CHANNEL, verification_msg)
                    
                    except Exception as e:
                        logger.debug(f"Error verifying {ip}: {e}")
                
                logger.info(f"Map verification complete: {online_count} online, {offline_count} offline")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in map verification loop: {e}")
                await asyncio.sleep(300)
    
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
        
        logger.info(f"Traceroute loop starting with interval {interval}s")
        logger.info(f"Initial trace_targets: {self.trace_targets}")
        
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
                            # Add ALL hops to local graph (for user's own visualization)
                            for i, hop in enumerate(hops):
                                self.local_graph.add_node(hop.ip_address, hop.hostname)
                                
                                if i > 0:
                                    prev_hop = hops[i-1]
                                    rtt_diff = abs(hop.rtt_ms - prev_hop.rtt_ms)
                                    self.local_graph.add_edge(
                                        prev_hop.ip_address,
                                        hop.ip_address,
                                        rtt_ms=rtt_diff
                                    )
                            
                            # Add ONLY public IPs to network graph (for IPFS sharing)
                            public_hops_discovered = []
                            for i, hop in enumerate(hops):
                                # Skip private IPs for shared graph
                                if not is_private_ip(hop.ip_address):
                                    self.network_graph.add_node(hop.ip_address, hop.hostname)
                                    public_hops_discovered.append(hop.ip_address)
                                    
                                    # Connect to previous public hop
                                    if i > 0:
                                        # Find previous public hop
                                        for j in range(i-1, -1, -1):
                                            prev_hop = hops[j]
                                            if not is_private_ip(prev_hop.ip_address):
                                                rtt_diff = abs(hop.rtt_ms - prev_hop.rtt_ms)
                                                self.network_graph.add_edge(
                                                    prev_hop.ip_address,
                                                    hop.ip_address,
                                                    rtt_ms=rtt_diff
                                                )
                                                break
                            
                            # Add discovered public IPs to trace_targets for future rounds
                            new_targets = []
                            for hop_ip in public_hops_discovered:
                                if hop_ip not in self.trace_targets and hop_ip != target_ip:
                                    self.trace_targets.add(hop_ip)
                                    new_targets.append(hop_ip)
                            
                            if new_targets:
                                logger.info(f"Added {len(new_targets)} new discovered IPs to trace queue")
                            
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
                            
                            # Update topology visualization after EVERY successful traceroute
                            await self._publish_topology()
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
                            if target_ip in self.local_graph.nodes:
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
        """
        Comprehensive bandwidth testing after traceroutes.
        Tests all discovered IPs sequentially with iperf3.
        """
        # Wait for initial traceroutes to complete
        await asyncio.sleep(120)
        
        bandwidth_config = self.config.get("bandwidth", {})
        test_interval = bandwidth_config.get("iperf3", {}).get("interval", 7200)
        
        while self.running:
            try:
                logger.info("=" * 60)
                logger.info("STARTING BANDWIDTH TEST CYCLE")
                logger.info("=" * 60)
                
                # Collect all IPs from the graph (use local_graph which has all IPs)
                all_ips = set(self.local_graph.nodes.keys())
                
                # Add peer IPs
                for peer in self.peer_nodes.values():
                    all_ips.add(peer.external_ip)
                
                if not all_ips:
                    logger.info("No IPs discovered yet, waiting...")
                    await asyncio.sleep(60)
                    continue
                
                logger.info(f"Found {len(all_ips)} unique IPs in topology")
                
                # Probe all IPs for iperf3 support
                logger.info("Probing for iperf3 servers...")
                testable_ips = self.bandwidth_manager.probe_targets(list(all_ips))
                
                if not testable_ips:
                    logger.warning("No iperf3 servers found")
                    await asyncio.sleep(test_interval)
                    continue
                
                logger.info(f"Found {len(testable_ips)} IPs with iperf3 servers")
                
                # Test all targets sequentially with traceroute paths
                logger.info(f"Starting sequential bandwidth tests to {len(testable_ips)} targets...")
                logger.info("Each test will traceroute first to get full path...")
                results = self.bandwidth_manager.test_all_targets(
                    testable_ips,
                    port=5201,
                    probe_first=False,  # Already probed
                    tracer=self.tracer  # Pass tracer to get paths
                )
                
                logger.info(f"Completed {len(results)} bandwidth tests")
                
                # Update graph with bandwidth results
                # Apply bandwidth to ALL edges in the traceroute path (tunnel bandwidth)
                for result, hops in results:
                    if not hops:
                        logger.warning(f"No hops for {result.target}, skipping bandwidth application")
                        continue
                        
                    logger.info(f"Applying bandwidth to path for {result.target}: {len(hops)} hops, {result.download_mbps:.2f} Mbps down / {result.upload_mbps:.2f} Mbps up")
                    
                    # Add ALL hops to local graph
                    for hop in hops:
                        self.local_graph.add_node(hop.ip_address, hop.hostname)
                    
                    # Apply bandwidth to ALL edges in the local graph path
                    # This represents the bottleneck bandwidth of the entire path
                    for i in range(len(hops) - 1):
                        hop1 = hops[i]
                        hop2 = hops[i + 1]
                        
                        # Calculate RTT difference for this edge
                        rtt_diff = abs(hop2.rtt_ms - hop1.rtt_ms) if hop2.rtt_ms and hop1.rtt_ms else None
                        
                        # Add edge to local graph with bandwidth (bottleneck for entire path)
                        self.local_graph.add_edge(
                            hop1.ip_address,
                            hop2.ip_address,
                            rtt_ms=rtt_diff,
                            bandwidth_down_mbps=result.download_mbps,
                            bandwidth_up_mbps=result.upload_mbps
                        )
                        
                        # Add to network graph only if both hops are public
                        if not is_private_ip(hop1.ip_address) and not is_private_ip(hop2.ip_address):
                            self.network_graph.add_node(hop1.ip_address, hop1.hostname)
                            self.network_graph.add_node(hop2.ip_address, hop2.hostname)
                            self.network_graph.add_edge(
                                hop1.ip_address,
                                hop2.ip_address,
                                rtt_ms=rtt_diff,
                                bandwidth_down_mbps=result.download_mbps,
                                bandwidth_up_mbps=result.upload_mbps
                            )
                        
                        logger.debug(f"Applied bandwidth to edge {hop1.ip_address} <-> {hop2.ip_address}: ↓{result.download_mbps:.2f} Mbps ↑{result.upload_mbps:.2f} Mbps")
                
                # Publish updated topology with bandwidth data
                await self._publish_topology()
                
                logger.info("=" * 60)
                logger.info(f"BANDWIDTH TEST CYCLE COMPLETE - Waiting {test_interval}s")
                logger.info("=" * 60)
                
                # Wait before next test cycle
                await asyncio.sleep(test_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in bandwidth test loop: {e}")
                await asyncio.sleep(300)
    
    async def _publish_topology(self):
        """Generate GEXF files and publish public topology to IPFS."""
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
            
            # Save LOCAL topology (includes private IPs) for web UI visualization
            local_gexf_path = output_dir / "topology_latest.gexf"
            local_generator = GEXFGenerator(self.local_graph)
            local_generator.generate(str(local_gexf_path), "Local Internet Topology (includes private IPs)")
            logger.info(f"Saved local topology: {len(self.local_graph.nodes)} nodes (includes private IPs)")
            
            # Save PUBLIC topology (public IPs only) for IPFS sharing
            network_gexf_path = output_dir / f"topology_public_{timestamp}.gexf"
            network_generator = GEXFGenerator(self.network_graph)
            network_generator.generate(str(network_gexf_path), "Public Internet Topology (public IPs only)")
            logger.info(f"Saved public topology: {len(self.network_graph.nodes)} nodes (public IPs only)")
            
            # Publish PUBLIC topology to IPFS network (fully P2P, no central server)
            try:
                cid = await self.ipfs_client.publish_topology(str(network_gexf_path))
                
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
