"""
Intermap - Distributed P2P Internet Topology Mapper
Copyright (c) 2025 Jay Wenden
Licensed under CC-BY-NC-SA 4.0
"""
"""
Bandwidth testing module - iperf3 and speedtest integration
"""
import logging
import subprocess
import json
import socket
import time
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, field

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
    timestamp: float = field(default_factory=time.time)
    peak: bool = False  # True if this is the peak result for this target


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
    
    @staticmethod
    def probe_server(host: str, port: int = 5201, timeout: int = 3) -> bool:
        """
        Probe if a host has an iperf3 server running.
        
        Args:
            host: Target IP or hostname
            port: iperf3 port (default: 5201)
            timeout: Connection timeout in seconds
            
        Returns:
            True if iperf3 server is reachable, False otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                logger.debug(f"iperf3 server detected at {host}:{port}")
                return True
            else:
                logger.debug(f"No iperf3 server at {host}:{port}")
                return False
        except Exception as e:
            logger.debug(f"Failed to probe {host}:{port}: {e}")
            return False
    
    def test_bandwidth(self, server: str, port: int = 5201, reverse: bool = False) -> Optional[BandwidthResult]:
        """
        Run iperf3 bandwidth test to a server.
        
        Args:
            server: Target server IP or hostname
            port: iperf3 server port (default: 5201)
            reverse: If True, test download (server sends to client)
            
        Returns:
            BandwidthResult with test results, or None if test fails
        """
        logger.info(f"Starting iperf3 test to {server}:{port} (reverse={reverse})")
        
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
            
            # Add reverse flag if testing download
            if reverse:
                cmd.append("-R")
            
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


class BandwidthTestManager:
    """
    Manages sequential bandwidth testing with peak result tracking.
    Ensures only one test runs at a time and tracks peak results per target.
    """
    
    def __init__(self, duration: int = 10):
        """
        Initialize bandwidth test manager.
        
        Args:
            duration: Duration for each iperf3 test in seconds
        """
        self.client = IPerf3Client(duration=duration)
        self.peak_results: Dict[str, BandwidthResult] = {}  # target -> peak result
        self.test_count = 0
    
    def probe_targets(self, targets: List[str], port: int = 5201) -> List[str]:
        """
        Probe multiple targets to find which have iperf3 servers.
        
        Args:
            targets: List of IP addresses or hostnames
            port: iperf3 port to probe
            
        Returns:
            List of targets that have iperf3 servers running
        """
        logger.info(f"Probing {len(targets)} targets for iperf3 servers...")
        available = []
        
        for target in targets:
            if IPerf3Client.probe_server(target, port):
                available.append(target)
        
        logger.info(f"Found {len(available)}/{len(targets)} targets with iperf3 servers")
        return available
    
    def test_target(self, target: str, port: int = 5201) -> Optional[BandwidthResult]:
        """
        Test bandwidth to a single target (sequential, one at a time).
        Updates peak results automatically.
        
        Args:
            target: IP address or hostname
            port: iperf3 port
            
        Returns:
            BandwidthResult if successful, None otherwise
        """
        logger.info(f"[Test {self.test_count + 1}] Testing {target}:{port}")
        
        # Run test
        result = self.client.test_bandwidth(target, port)
        
        if result:
            self.test_count += 1
            
            # Update peak result if this is better
            if target not in self.peak_results:
                result.peak = True
                self.peak_results[target] = result
                logger.info(f"New peak for {target}: {result.download_mbps:.2f} Mbps")
            else:
                prev_peak = self.peak_results[target]
                current_total = result.download_mbps + result.upload_mbps
                peak_total = prev_peak.download_mbps + prev_peak.upload_mbps
                
                if current_total > peak_total:
                    # This is a new peak
                    prev_peak.peak = False
                    result.peak = True
                    self.peak_results[target] = result
                    logger.info(f"New peak for {target}: {result.download_mbps:.2f} Mbps (previous: {prev_peak.download_mbps:.2f})")
                else:
                    logger.info(f"Not a peak for {target}: {result.download_mbps:.2f} Mbps (peak: {prev_peak.download_mbps:.2f})")
        
        return result
    
    def test_all_targets(self, targets: List[str], port: int = 5201, probe_first: bool = True) -> List[BandwidthResult]:
        """
        Test bandwidth to all targets sequentially.
        
        Args:
            targets: List of IP addresses or hostnames
            port: iperf3 port
            probe_first: If True, probe targets before testing
            
        Returns:
            List of BandwidthResult objects (successful tests only)
        """
        if probe_first:
            # Filter to only targets with iperf3 servers
            targets = self.probe_targets(targets, port)
        
        if not targets:
            logger.warning("No targets available for testing")
            return []
        
        logger.info(f"Testing {len(targets)} targets sequentially...")
        results = []
        
        for i, target in enumerate(targets, 1):
            logger.info(f"Progress: {i}/{len(targets)}")
            result = self.test_target(target, port)
            
            if result:
                results.append(result)
            
            # Brief pause between tests to avoid congestion
            if i < len(targets):
                time.sleep(2)
        
        logger.info(f"Completed {len(results)}/{len(targets)} bandwidth tests")
        return results
    
    def get_peak_results(self) -> List[BandwidthResult]:
        """
        Get all peak results.
        
        Returns:
            List of peak BandwidthResult objects
        """
        return list(self.peak_results.values())
    
    def get_peak_for_target(self, target: str) -> Optional[BandwidthResult]:
        """
        Get peak result for a specific target.
        
        Args:
            target: IP address or hostname
            
        Returns:
            BandwidthResult if target has been tested, None otherwise
        """
        return self.peak_results.get(target)


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
    
    print("\nTesting probe functionality...")
    has_iperf = IPerf3Client.probe_server("ping.online.net", 5201)
    print(f"ping.online.net has iperf3: {has_iperf}")
