"""
Main entry point for running a topology mapper node
"""
import asyncio
import logging
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.node.node import TopologyNode
from src.ipfs.client import IPFSClient


def setup_logging(verbose: bool = False):
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('topology_node.log')
        ]
    )


async def main():
    """Main entry point for the topology mapper node."""
    parser = argparse.ArgumentParser(
        description='Distributed Internet Topology Mapper Node'
    )
    parser.add_argument(
        '--node-id',
        help='Unique identifier for this node (auto-generated if not provided)'
    )
    parser.add_argument(
        '--ipfs-api',
        default='/ip4/127.0.0.1/tcp/5001',
        help='IPFS API address (default: /ip4/127.0.0.1/tcp/5001)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    setup_logging(args.verbose)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Distributed Topology Mapper Node")
    
    # Create and start node
    node = TopologyNode(node_id=args.node_id)
    
    try:
        await node.start()
        
        # Keep running until interrupted
        while node.running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Error running node: {e}", exc_info=True)
    finally:
        await node.stop()
        logger.info("Node stopped")


if __name__ == "__main__":
    asyncio.run(main())
