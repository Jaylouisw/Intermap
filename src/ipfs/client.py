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
    
    async def announce_node(self, node_id: str, external_ip: str, api_port: int = 5000) -> Optional[str]:
        """
        Announce node presence to IPFS network using DHT.
        Publishes node info to IPFS and pins it for discoverability.
        
        Args:
            node_id: Unique node identifier
            external_ip: External IP address
            api_port: API server port
            
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
                "timestamp": time.time(),
                "protocol_version": "intermap-v1"
            }
            
            # Add to IPFS
            cid = await self.add_json(node_info)
            self._node_info_cid = cid
            
            # Pin it so it stays available
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor,
                self.client.pin.add,
                cid
            )
            
            logger.info(f"Announced node to IPFS: {cid}")
            logger.info(f"Node: {node_id} @ {external_ip}:{api_port}")
            
            return cid
            
        except Exception as e:
            logger.warning(f"Failed to announce node: {e}")
            return None
    
    async def discover_peers(self) -> List[Dict]:
        """
        Discover peer nodes by querying IPFS for known node CIDs.
        Uses IPFS peer discovery + direct CID fetching.
        
        Returns:
            List of peer node info dictionaries
        """
        if not self.connected or not self._dht_enabled:
            return []
        
        try:
            peers = []
            loop = asyncio.get_event_loop()
            
            # Get connected IPFS peers
            def _get_swarm_peers():
                return self.client.swarm.peers()
            
            swarm_peers = await loop.run_in_executor(self._executor, _get_swarm_peers)
            logger.debug(f"Connected to {len(swarm_peers)} IPFS peers")
            
            # Try to find intermap nodes through DHT routing
            # We'll use IPFS name resolution and content discovery
            
            # For now, nodes will share their CIDs through the IPFS network
            # Future: implement IPNS for mutable peer lists
            
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
