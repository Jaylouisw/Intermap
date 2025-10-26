"""
Bandwidth testing module - iperf3 and speedtest integration
"""
import logging
import subprocess
import json
from typing import Dict, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BandwidthResult:
    """Represents bandwidth test results."""
    target: str
    download_mbps: float
    upload_mbps: float
    latency_ms: Optional[float] = None
    jitter_ms: Optional[float] = None
    test_type: str = "iperf3"  # iperf3 or speedtest


class IPerf3Client:
    """
    Client for running iperf3 bandwidth tests.
    
    Tests bandwidth between nodes or to public iperf3 servers.
    """
    
    def __init__(self, duration: int = 10, parallel: int = 1):
        """
        Initialize iperf3 client.
        
        Args:
            duration: Test duration in seconds
            parallel: Number of parallel streams
        """
        self.duration = duration
        self.parallel = parallel
    
    def test_bandwidth(self, server: str, port: int = 5201) -> Optional[BandwidthResult]:
        """
        Run iperf3 bandwidth test to a server.
        
        Args:
            server: Target server IP or hostname
            port: iperf3 server port (default: 5201)
            
        Returns:
            BandwidthResult with test results, or None if test fails
        """
        logger.info(f"Starting iperf3 test to {server}:{port}")
        
        try:
            # Run iperf3 client with JSON output
            cmd = [
                "iperf3",
                "-c", server,
                "-p", str(port),
                "-t", str(self.duration),
                "-P", str(self.parallel),
                "-J"  # JSON output
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.duration + 10
            )
            
            if result.returncode != 0:
                logger.error(f"iperf3 failed: {result.stderr}")
                return None
            
            # Parse JSON output
            data = json.loads(result.stdout)
            
            # Extract bandwidth data
            download_bps = data.get("end", {}).get("sum_received", {}).get("bits_per_second", 0)
            upload_bps = data.get("end", {}).get("sum_sent", {}).get("bits_per_second", 0)
            
            # Convert to Mbps
            download_mbps = download_bps / 1_000_000
            upload_mbps = upload_bps / 1_000_000
            
            logger.info(f"iperf3 results: ↓ {download_mbps:.2f} Mbps, ↑ {upload_mbps:.2f} Mbps")
            
            return BandwidthResult(
                target=server,
                download_mbps=download_mbps,
                upload_mbps=upload_mbps,
                test_type="iperf3"
            )
            
        except FileNotFoundError:
            logger.error("iperf3 not found. Install with: apt install iperf3 (Linux) or choco install iperf3 (Windows)")
            return None
        except subprocess.TimeoutExpired:
            logger.error(f"iperf3 test timed out after {self.duration + 10}s")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse iperf3 output: {e}")
            return None
        except Exception as e:
            logger.error(f"iperf3 test failed: {e}")
            return None


class SpeedtestClient:
    """
    Client for running speedtest-cli tests.
    
    Tests bandwidth to nearest speedtest.net server.
    """
    
    def test_bandwidth(self) -> Optional[BandwidthResult]:
        """
        Run speedtest-cli bandwidth test.
        
        Returns:
            BandwidthResult with test results, or None if test fails
        """
        logger.info("Starting speedtest...")
        
        try:
            # Run speedtest-cli with JSON output
            cmd = ["speedtest-cli", "--json"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                logger.error(f"speedtest failed: {result.stderr}")
                return None
            
            # Parse JSON output
            data = json.loads(result.stdout)
            
            # Extract data
            download_bps = data.get("download", 0)
            upload_bps = data.get("upload", 0)
            latency_ms = data.get("ping", 0)
            server_host = data.get("server", {}).get("host", "speedtest.net")
            
            # Convert to Mbps
            download_mbps = download_bps / 1_000_000
            upload_mbps = upload_bps / 1_000_000
            
            logger.info(f"Speedtest results: ↓ {download_mbps:.2f} Mbps, ↑ {upload_mbps:.2f} Mbps, latency: {latency_ms:.1f}ms")
            
            return BandwidthResult(
                target=server_host,
                download_mbps=download_mbps,
                upload_mbps=upload_mbps,
                latency_ms=latency_ms,
                test_type="speedtest"
            )
            
        except FileNotFoundError:
            logger.error("speedtest-cli not found. Install with: pip install speedtest-cli")
            return None
        except subprocess.TimeoutExpired:
            logger.error("Speedtest timed out after 60s")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse speedtest output: {e}")
            return None
        except Exception as e:
            logger.error(f"Speedtest failed: {e}")
            return None


# Public iperf3 servers for testing
PUBLIC_IPERF3_SERVERS = [
    {"host": "ping.online.net", "port": 5201, "location": "France"},
    {"host": "iperf.he.net", "port": 5201, "location": "USA"},
    {"host": "speedtest.serverius.net", "port": 5002, "location": "Netherlands"},
    {"host": "bouygues.iperf.fr", "port": 5200, "location": "France"},
]


def test_public_servers(max_servers: int = 3) -> List[BandwidthResult]:
    """
    Test bandwidth to multiple public iperf3 servers.
    
    Args:
        max_servers: Maximum number of servers to test
        
    Returns:
        List of BandwidthResult objects
    """
    results = []
    client = IPerf3Client(duration=5)  # Shorter duration for multiple tests
    
    for server_info in PUBLIC_IPERF3_SERVERS[:max_servers]:
        host = server_info["host"]
        port = server_info["port"]
        location = server_info["location"]
        
        logger.info(f"Testing {host} ({location})...")
        
        result = client.test_bandwidth(host, port)
        if result:
            results.append(result)
    
    return results


if __name__ == "__main__":
    # Test bandwidth functionality
    logging.basicConfig(level=logging.INFO)
    
    print("Testing iperf3...")
    client = IPerf3Client()
    result = client.test_bandwidth("ping.online.net")
    if result:
        print(f"Download: {result.download_mbps:.2f} Mbps")
        print(f"Upload: {result.upload_mbps:.2f} Mbps")
    
    print("\nTesting speedtest...")
    speedtest = SpeedtestClient()
    result = speedtest.test_bandwidth()
    if result:
        print(f"Download: {result.download_mbps:.2f} Mbps")
        print(f"Upload: {result.upload_mbps:.2f} Mbps")
