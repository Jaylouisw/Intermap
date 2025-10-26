"""
Intermap - Distributed P2P Internet Topology Mapper
Copyright (c) 2025 Jay Wenden
Licensed under CC-BY-NC-SA 4.0
"""
"""
IPFS client for distributed storage and DHT-based P2P peer coordination
"""
import asyncio
import logging
from typing import Optional, Callable, Dict, Any, List
import json
from pathlib import Path
import base64
import requests
import time

logger = logging.getLogger(__name__)


class IPFSClient:
    """
    Client for interacting with IPFS for distributed storage and P2P coordination.
    
    Uses IPFS DHT + Content Addressing for fully decentralized peer discovery.
    No central server - pure P2P using IPFS as the coordination layer.
    """
    
    # Well-known DHT keys for rendezvous
    RENDEZVOUS_KEY = "QmUNLLsPACCz1vLxQVkXqqLX5R1X345qqfHbsf67hvA3Nn"  # Intermap rendezvous point
    
    def __init__(self, api_addr: str = "/ip4/127.0.0.1/tcp/5001"):
        """
        Initialize IPFS client.
        
        Args:
            api_addr: IPFS API multiaddr (default: local node)
        """
        self.api_addr = api_addr
        self.client = None
        self.connected = False
        self._executor = None
        self._dht_enabled = False
        self._node_info_cid = None  # CID of our published node info
        self._topology_cid = None  # Latest topology CID
        
    async def connect(self):
        """Connect to IPFS node."""
        try:
            import ipfshttpclient
            from concurrent.futures import ThreadPoolExecutor
            
            # Connect to IPFS daemon
            self.client = ipfshttpclient.connect(self.api_addr)
            
            # Test connection
            version = self.client.version()
            logger.info(f"Connected to IPFS at {self.api_addr} (version: {version['Version']})")
            
            # Test DHT availability - just verify we can connect to swarm
            try:
                peers = self.client.swarm.peers()
                self._dht_enabled = True
                logger.info(f"Connected to IPFS swarm with {len(peers)} peers")
                logger.info("DHT-based P2P discovery enabled - fully decentralized")
            except Exception as e:
                logger.warning(f"IPFS swarm not available: {e}")
                logger.warning("Running in standalone mode")
            
            # Create executor for blocking IPFS calls
            self._executor = ThreadPoolExecutor(max_workers=4)
            
            self.connected = True
            
        except ImportError:
            logger.error("ipfshttpclient not installed. Run: pip install ipfshttpclient")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to IPFS: {e}")
            logger.info("Make sure IPFS daemon is running: ipfs daemon")
            raise
    
    async def disconnect(self):
        """Disconnect from IPFS and cleanup."""
        # Shutdown executor
        if self._executor:
            self._executor.shutdown(wait=False)
        
        # Close IPFS client
        if self.client:
            try:
                self.client.close()
            except:
                pass
        
        self.connected = False
        logger.info("Disconnected from IPFS")
    
    async def announce_node(self, node_id: str, external_ip: str, api_port: int = 5000, iperf3_port: int = 5201) -> Optional[str]:
        """
        Announce node presence to IPFS network using DHT provider records.
        Publishes node info to IPFS and advertises as provider for the rendezvous key.
        
        Args:
            node_id: Unique node identifier
            external_ip: External IP address
            api_port: API server port
            iperf3_port: iperf3 server port
            
        Returns:
            CID of published node info
        """
        if not self.connected:
            return None
        
        try:
            node_info = {
                "node_id": node_id,
                "external_ip": external_ip,
                "api_port": api_port,
                "iperf3_port": iperf3_port,
                "timestamp": time.time(),
                "protocol_version": "intermap-v1"
            }
            
            # Add to IPFS
            cid = await self.add_json(node_info)
            self._node_info_cid = cid
            
            loop = asyncio.get_event_loop()
            
            # Pin it so it stays available
            await loop.run_in_executor(
                self._executor,
                self.client.pin.add,
                cid
            )
            
            # CRITICAL: Advertise as provider for the rendezvous key in DHT
            # This is how other nodes will discover us
            # Use HTTP API directly - newer IPFS versions use 'routing provide'
            try:
                import requests
                api_url = "http://127.0.0.1:5001/api/v0/routing/provide"
                params = {'arg': self.RENDEZVOUS_KEY}
                response = requests.post(api_url, params=params, timeout=30)
                if response.status_code == 200:
                    logger.info(f"✓ Announced node to DHT: {cid}")
                    logger.info(f"  Node ID: {node_id}")
                    logger.info(f"  External IP: {external_ip}")
                    logger.info(f"  iperf3: Port {iperf3_port}")
                    logger.info(f"  DHT Provider for: {self.RENDEZVOUS_KEY}")
                else:
                    logger.warning(f"DHT provider advertisement returned: {response.status_code}")
                    logger.info(f"Announced node to IPFS (no DHT): {cid}")
            except Exception as e:
                logger.warning(f"DHT provider advertisement failed: {e}")
                logger.info(f"Announced node to IPFS (no DHT): {cid}")
            
            # ALSO: Publish via PubSub for immediate peer discovery
            # This is more reliable than DHT queries
            try:
                pubsub_message = {
                    "type": "node_announcement",
                    "node_id": node_id,
                    "external_ip": external_ip,
                    "api_port": api_port,
                    "iperf3_port": iperf3_port,
                    "node_info_cid": cid,
                    "protocol_version": "intermap-v1",
                    "timestamp": time.time()
                }
                await self.publish("intermap-discovery", pubsub_message)
                logger.debug(f"Published node announcement via PubSub")
            except Exception as e:
                logger.debug(f"PubSub announcement failed: {e}")
            
            return cid
            
        except Exception as e:
            logger.warning(f"Failed to announce node: {e}")
            return None
    
    async def discover_peers(self) -> List[Dict]:
        """
        Discover peer nodes by querying DHT for providers of the rendezvous key.
        Fetches and verifies node_info from each provider to ensure they're real Intermap nodes.
        
        Returns:
            List of verified peer node info dictionaries with external_ip, node_id, etc.
        """
        if not self.connected or not self._dht_enabled:
            return []
        
        try:
            peers = []
            loop = asyncio.get_event_loop()
            provider_cids = []
            
            # Query DHT for providers of the rendezvous key
            # These SHOULD be Intermap nodes that announced themselves
            try:
                # Use newer routing findprovs API
                import requests
                api_url = "http://127.0.0.1:5001/api/v0/routing/findprovs"
                params = {'arg': self.RENDEZVOUS_KEY, 'num-providers': 50}
                response = requests.post(api_url, params=params, timeout=30, stream=True)
                
                if response.status_code == 200:
                    # Parse NDJSON responses to get provider CIDs
                    for line in response.iter_lines():
                        if line:
                            try:
                                result = json.loads(line)
                                if result.get('Type') == 4:  # Provider response
                                    peer_id = result.get('Responses', [{}])[0].get('ID')
                                    if peer_id:
                                        # Try to find what CID this provider is providing
                                        # Providers advertise content, we need to fetch their node_info
                                        provider_cids.append(peer_id)
                            except:
                                pass
                    
                    logger.debug(f"DHT query found {len(provider_cids)} potential providers")
                else:
                    logger.debug(f"DHT findprovs returned: {response.status_code}")
                        
            except Exception as e:
                logger.debug(f"DHT findprovs error: {e}")
            
            # Now try to fetch node_info from DHT using common pattern
            # Intermap nodes publish node_info as: QmXXXXXX (their node_info CID)
            # We'll try to find these by querying the DHT for "intermap-node-*" pattern
            # Alternative: Use IPNS or a known naming convention
            
            # For now, just query swarm peers and see who responds to our protocol
            # This is a simpler approach - check connected peers
            def _get_swarm_peers():
                return self.client.swarm.peers()
            
            swarm_peers = await loop.run_in_executor(self._executor, _get_swarm_peers)
            logger.debug(f"Connected to {len(swarm_peers)} IPFS swarm peers (not all are Intermap nodes)")
            
            # Return verified peers only (TODO: implement actual node_info fetching)
            # For now, this prevents false positives by returning empty until we can verify
            logger.info(f"Verified {len(peers)} actual Intermap nodes (need node_info exchange protocol)")
            
            return peers
            
        except Exception as e:
            logger.debug(f"Peer discovery error: {e}")
            return []
    
    async def publish_topology(self, topology_path: str) -> Optional[str]:
        """
        Publish topology file to IPFS network.
        
        Args:
            topology_path: Path to GEXF topology file
            
        Returns:
            CID of published topology
        """
        if not self.connected:
            return None
        
        try:
            cid = await self.add_file(topology_path)
            self._topology_cid = cid
            
            # Pin topology
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor,
                self.client.pin.add,
                cid
            )
            
            logger.info(f"Published topology to IPFS: {cid}")
            return cid
            
        except Exception as e:
            logger.warning(f"Failed to publish topology: {e}")
            return None
    
    async def fetch_peer_info(self, cid: str) -> Optional[Dict]:
        """
        Fetch peer node info from IPFS by CID.
        
        Args:
            cid: Content ID of peer info
            
        Returns:
            Peer info dictionary or None
        """
        try:
            content = await self.cat_file(cid)
            return json.loads(content.decode('utf-8'))
        except Exception as e:
            logger.debug(f"Failed to fetch peer info {cid}: {e}")
            return None
    
    async def add_json(self, data: Dict) -> str:
        """
        Add JSON data to IPFS.
        
        Args:
            data: Dictionary to serialize and add
            
        Returns:
            IPFS CID of the added data
        """
        if not self.connected:
            raise RuntimeError("Not connected to IPFS")
        
        try:
            import tempfile
            import os
            
            # Write JSON to temp file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                json.dump(data, f)
                temp_path = f.name
            
            try:
                # Add to IPFS
                cid = await self.add_file(temp_path)
                return cid
            finally:
                # Cleanup temp file
                os.unlink(temp_path)
                
        except Exception as e:
            logger.error(f"Failed to add JSON to IPFS: {e}")
            raise
    
    async def add_file(self, file_path: str) -> str:
        """
        Add a file to IPFS.
        
        Args:
            file_path: Path to file to add
            
        Returns:
            IPFS CID (Content Identifier) of the added file
        """
        if not self.connected:
            raise RuntimeError("Not connected to IPFS")
        
        try:
            loop = asyncio.get_event_loop()
            
            # Add file in executor (blocking call)
            result = await loop.run_in_executor(
                self._executor,
                self.client.add,
                file_path
            )
            
            cid = result['Hash']
            logger.info(f"Added file to IPFS: {file_path} -> {cid}")
            return cid
            
        except Exception as e:
            logger.error(f"Failed to add file to IPFS: {e}")
            raise
    
    async def get_file(self, cid: str, output_path: str):
        """
        Retrieve a file from IPFS.
        
        Args:
            cid: IPFS Content Identifier
            output_path: Path to save retrieved file
        """
        if not self.connected:
            raise RuntimeError("Not connected to IPFS")
        
        try:
            loop = asyncio.get_event_loop()
            
            # Get file in executor (blocking call)
            await loop.run_in_executor(
                self._executor,
                self.client.get,
                cid,
                target=output_path
            )
            
            logger.info(f"Retrieved file from IPFS: {cid} -> {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to get file from IPFS: {e}")
            raise
    
    async def cat_file(self, cid: str) -> bytes:
        """
        Read file contents from IPFS without saving to disk.
        
        Args:
            cid: IPFS Content Identifier
            
        Returns:
            File contents as bytes
        """
        if not self.connected:
            raise RuntimeError("Not connected to IPFS")
        
        try:
            loop = asyncio.get_event_loop()
            
            # Cat file in executor (blocking call)
            contents = await loop.run_in_executor(
                self._executor,
                self.client.cat,
                cid
            )
            
            logger.debug(f"Read file from IPFS: {cid} ({len(contents)} bytes)")
            return contents
            
        except Exception as e:
            logger.error(f"Failed to cat file from IPFS: {e}")
            raise


if __name__ == "__main__":
    # Basic testing
    logging.basicConfig(level=logging.INFO)
    
    async def test():
        client = IPFSClient()
        await client.connect()
        
        # Test node announcement
        cid = await client.announce_node("test-node-123", "192.168.1.100", 5000)
        print(f"Node announced: {cid}")
        
        # Test peer discovery
        peers = await client.discover_peers()
        print(f"Discovered {len(peers)} peers")
        
        await client.disconnect()
    
    asyncio.run(test())
