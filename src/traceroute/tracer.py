"""
Traceroute implementation using scapy or system tools
"""
import logging
import platform
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.utils import is_public_ip, filter_private_ips

logger = logging.getLogger(__name__)


@dataclass
class Hop:
    """Represents a single hop in a traceroute."""
    hop_number: int
    ip_address: str
    hostname: Optional[str]
    rtt_ms: float  # Round-trip time in milliseconds
    

class Traceroute:
    """
    Performs traceroute operations to discover network paths.
    
    Supports multiple backends:
    - System traceroute command (Windows/Linux/Mac)
    - Scapy for programmatic control
    
    PRIVACY: Only public IPs are included in results.
    """
    
    def __init__(self, max_hops: int = 30, timeout: int = 5, filter_private: bool = True, verify_reachable: bool = True):
        """
        Initialize traceroute engine.
        
        Args:
            max_hops: Maximum number of hops to trace
            timeout: Timeout in seconds for each hop
            filter_private: If True, exclude private IPs from results (default: True)
            verify_reachable: If True, ping target before traceroute to verify it's online
        """
        self.max_hops = max_hops
        self.timeout = timeout
        self.filter_private = filter_private
        self.verify_reachable = verify_reachable
        self.os_type = platform.system()
        
    def trace(self, target: str, filter_private_override: Optional[bool] = None) -> List[Hop]:
        """
        Perform traceroute to target host.
        
        Args:
            target: Target IP address or hostname
            filter_private_override: Override filter_private setting for this trace
            
        Returns:
            List of Hop objects representing the network path (private IPs filtered)
        """
        logger.info(f"Starting traceroute to {target}")
        
        # Check if target is public
        if not is_public_ip(target):
            logger.warning(f"Target {target} is not a public IP address - aborting traceroute")
            return []
        
        # Verify target is reachable before tracing
        if self.verify_reachable:
            if not self._ping_target(target):
                logger.warning(f"Target {target} is not reachable (ping failed) - skipping traceroute")
                return []
        
        try:
            if self.os_type == "Windows":
                hops = self._trace_windows(target)
            elif self.os_type in ["Linux", "Darwin"]:
                hops = self._trace_unix(target)
            else:
                raise NotImplementedError(f"Traceroute not implemented for {self.os_type}")
            
            # Filter private IPs if enabled
            should_filter = filter_private_override if filter_private_override is not None else self.filter_private
            if should_filter:
                filtered_hops = [h for h in hops if is_public_ip(h.ip_address)]
                logger.info(f"Filtered {len(hops) - len(filtered_hops)} private hops from results")
                return filtered_hops
            
            return hops
            
        except Exception as e:
            logger.error(f"Traceroute failed: {e}")
            return []
    
    def _ping_target(self, target: str) -> bool:
        """
        Ping target to verify it's reachable before traceroute.
        
        Args:
            target: Target IP or hostname
            
        Returns:
            True if target responds to ping, False otherwise
        """
        try:
            if self.os_type == "Windows":
                # ping -n 2 -w 2000 (2 packets, 2 second timeout)
                cmd = ["ping", "-n", "2", "-w", "2000", target]
            else:
                # ping -c 2 -W 2 (2 packets, 2 second timeout)
                cmd = ["ping", "-c", "2", "-W", "2", target]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Check if ping was successful
            if result.returncode == 0:
                logger.info(f"Ping to {target} successful - proceeding with traceroute")
                return True
            else:
                logger.info(f"Ping to {target} failed - target appears offline")
                return False
                
        except (subprocess.TimeoutExpired, Exception) as e:
            logger.warning(f"Ping check failed for {target}: {e}")
            # If ping fails, allow traceroute to proceed (might be ICMP blocked)
            return True
    
    def _trace_windows(self, target: str) -> List[Hop]:
        """Perform traceroute using Windows tracert command."""
        cmd = ["tracert", "-h", str(self.max_hops), "-w", str(self.timeout * 1000), target]
        return self._parse_tracert_output(self._run_command(cmd, target))
    
    def _trace_unix(self, target: str) -> List[Hop]:
        """Perform traceroute using Unix traceroute command."""
        cmd = ["traceroute", "-m", str(self.max_hops), "-w", str(self.timeout), target]
        return self._parse_traceroute_output(self._run_command(cmd, target))
    
    def _run_command(self, cmd: List[str], target: str) -> str:
        """
        Run a system command and return output.
        
        Args:
            cmd: Command to run
            target: Target IP/hostname being traced (used to determine timeout)
        
        Returns:
            Command output as string
        """
        try:
            # If target pinged successfully and verify_reachable is enabled, 
            # skip the timeout to let traceroute complete naturally
            if self.verify_reachable:
                # No subprocess timeout - let traceroute finish
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=None
                )
            else:
                # Use timeout if ping verification is disabled
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=max(30, self.max_hops)  # At least 30 seconds, or 1 second per hop
                )
            return result.stdout
        except subprocess.TimeoutExpired as e:
            logger.warning(f"Traceroute command timed out: {' '.join(cmd)}")
            # Return partial output if available
            if e.stdout:
                logger.info(f"Returning partial traceroute output")
                return e.stdout.decode() if isinstance(e.stdout, bytes) else e.stdout
            return ""
        except FileNotFoundError:
            logger.error(f"Traceroute command not found: {cmd[0]}")
            return ""
    
    def _parse_tracert_output(self, output: str) -> List[Hop]:
        """
        Parse Windows tracert output.
        
        Format examples:
          1    <1 ms    <1 ms    <1 ms  192.168.1.1
          2     5 ms     4 ms     5 ms  10.0.0.1
          3    15 ms    14 ms    16 ms  edge-router.isp.com [203.0.113.1]
          4     *        *        *     Request timed out.
        """
        hops = []
        lines = output.strip().split('\n')
        
        import re
        
        for line in lines:
            line = line.strip()
            
            # Skip header lines
            if not line or 'Tracing route' in line or 'over a maximum' in line:
                continue
            
            # Match hop line: "  1    <1 ms    <1 ms    <1 ms  192.168.1.1"
            # Or with hostname: "  3    15 ms    14 ms    16 ms  router.example.com [8.8.8.8]"
            match = re.match(r'\s*(\d+)\s+(?:(<?\d+)\s*ms\s+(?:(<?\d+)\s*ms\s+)?(?:(<?\d+)\s*ms\s+)?)?(.+)', line)
            
            if not match:
                continue
            
            hop_num = int(match.group(1))
            remaining = match.group(5).strip()
            
            # Check for timeout
            if '*' in remaining or 'Request timed out' in remaining:
                continue
            
            # Extract IP and hostname
            hostname = None
            ip_address = None
            
            # Check for format: "hostname [ip]"
            bracket_match = re.search(r'\[([0-9.]+)\]', remaining)
            if bracket_match:
                ip_address = bracket_match.group(1)
                # Extract hostname (everything before the bracket)
                hostname = remaining[:remaining.index('[')].strip()
            else:
                # Just an IP address
                ip_match = re.search(r'([0-9.]+)', remaining)
                if ip_match:
                    ip_address = ip_match.group(1)
            
            if not ip_address:
                continue
            
            # Calculate average RTT from the times
            rtts = []
            for i in [2, 3, 4]:
                if match.group(i):
                    time_str = match.group(i).replace('<', '')
                    try:
                        rtts.append(float(time_str))
                    except ValueError:
                        pass
            
            avg_rtt = sum(rtts) / len(rtts) if rtts else 0.0
            
            hops.append(Hop(
                hop_number=hop_num,
                ip_address=ip_address,
                hostname=hostname,
                rtt_ms=avg_rtt
            ))
        
        return hops
    
    def _parse_traceroute_output(self, output: str) -> List[Hop]:
        """
        Parse Unix traceroute output.
        
        Format examples:
         1  gateway (192.168.1.1)  1.234 ms  1.123 ms  1.456 ms
         2  10.0.0.1 (10.0.0.1)  5.678 ms  5.432 ms  5.890 ms
         3  * * *
         4  edge-router.isp.com (203.0.113.1)  15.234 ms  14.567 ms  16.789 ms
        """
        hops = []
        lines = output.strip().split('\n')
        
        import re
        
        for line in lines:
            line = line.strip()
            
            # Skip header lines
            if not line or 'traceroute to' in line.lower():
                continue
            
            # Match hop line: " 1  gateway (192.168.1.1)  1.234 ms  1.123 ms  1.456 ms"
            match = re.match(r'\s*(\d+)\s+(.+)', line)
            
            if not match:
                continue
            
            hop_num = int(match.group(1))
            remaining = match.group(2).strip()
            
            # Check for timeout
            if '*' in remaining and '(' not in remaining:
                continue
            
            # Extract IP and hostname
            hostname = None
            ip_address = None
            
            # Format: "hostname (ip) time ms ..."
            paren_match = re.search(r'([^\s]+)\s+\(([0-9.]+)\)', remaining)
            if paren_match:
                hostname = paren_match.group(1)
                ip_address = paren_match.group(2)
            else:
                # Just IP: "192.168.1.1  1.234 ms"
                ip_match = re.search(r'([0-9.]+)', remaining)
                if ip_match:
                    ip_address = ip_match.group(1)
            
            if not ip_address:
                continue
            
            # Extract RTT values (multiple times in ms)
            rtts = []
            for time_match in re.finditer(r'([0-9.]+)\s*ms', remaining):
                try:
                    rtts.append(float(time_match.group(1)))
                except ValueError:
                    pass
            
            avg_rtt = sum(rtts) / len(rtts) if rtts else 0.0
            
            hops.append(Hop(
                hop_number=hop_num,
                ip_address=ip_address,
                hostname=hostname,
                rtt_ms=avg_rtt
            ))
        
        return hops


def trace_to_target(target: str, filter_private: bool = True) -> Dict:
    """
    Convenience function to perform a traceroute and return results as dict.
    
    Args:
        target: Target IP or hostname
        filter_private: Filter out private IPs (default: True)
        
    Returns:
        Dictionary containing traceroute results (private IPs filtered)
    """
    tracer = Traceroute(filter_private=filter_private)
    hops = tracer.trace(target)
    
    return {
        "target": target,
        "hop_count": len(hops),
        "hops": [
            {
                "hop": h.hop_number,
                "ip": h.ip_address,
                "hostname": h.hostname,
                "rtt": h.rtt_ms
            }
            for h in hops
        ]
    }


def trace_subnet(subnet: str, max_targets: int = 50) -> List[Dict]:
    """
    Perform traceroutes to all IPs in a subnet.
    
    SECURITY: Only traces public subnets. Private subnets are rejected.
    
    Args:
        subnet: Subnet in CIDR notation (e.g., "8.8.8.0/28")
        max_targets: Maximum number of IPs to trace (default: 50)
        
    Returns:
        List of traceroute results for each IP
    """
    from src.utils import expand_subnet
    
    logger.info(f"Starting subnet trace: {subnet}")
    
    ips = expand_subnet(subnet)
    
    if not ips:
        logger.error(f"Invalid or too large subnet: {subnet}")
        return []
    
    # Filter to only public IPs
    public_ips = filter_private_ips(ips)
    
    if not public_ips:
        logger.warning(f"No public IPs found in subnet {subnet}")
        return []
    
    # Limit number of targets
    if len(public_ips) > max_targets:
        logger.warning(f"Subnet has {len(public_ips)} IPs, limiting to {max_targets}")
        public_ips = public_ips[:max_targets]
    
    results = []
    for ip in public_ips:
        try:
            result = trace_to_target(ip)
            if result['hop_count'] > 0:
                results.append(result)
        except Exception as e:
            logger.error(f"Failed to trace {ip}: {e}")
    
    logger.info(f"Completed subnet trace: {len(results)}/{len(public_ips)} successful")
    return results



if __name__ == "__main__":
    # Test traceroute
    logging.basicConfig(level=logging.INFO)
    result = trace_to_target("8.8.8.8")
    print(f"Traced {result['hop_count']} hops to {result['target']}")
