"""
NAT detection and firewall handling utilities
"""
import socket
import logging
from typing import Optional, Tuple
import requests

logger = logging.getLogger(__name__)


def detect_nat() -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Detect if behind NAT by comparing local and external IPs.
    
    Returns:
        (is_behind_nat, local_ip, external_ip)
    """
    try:
        # Get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # Get external IP
        external_ip = None
        services = [
            "https://api.ipify.org",
            "https://ifconfig.me/ip",
            "https://icanhazip.com"
        ]
        
        for service in services:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    external_ip = response.text.strip()
                    break
            except:
                continue
        
        if not external_ip:
            logger.warning("Could not detect external IP")
            return False, local_ip, None
        
        # Compare IPs
        is_behind_nat = (local_ip != external_ip)
        
        if is_behind_nat:
            logger.info(f"Behind NAT: local={local_ip}, external={external_ip}")
        else:
            logger.info(f"Direct connection: {external_ip}")
        
        return is_behind_nat, local_ip, external_ip
        
    except Exception as e:
        logger.error(f"Error detecting NAT: {e}")
        return False, None, None


def check_port_open(host: str, port: int, timeout: int = 5) -> bool:
    """
    Check if a port is open/reachable.
    
    Args:
        host: Host to check
        port: Port number
        timeout: Timeout in seconds
        
    Returns:
        True if port is open/reachable
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        logger.debug(f"Port check failed for {host}:{port} - {e}")
        return False


def check_traceroute_capability() -> bool:
    """
    Check if traceroute is available and working.
    
    Returns:
        True if traceroute commands work
    """
    import platform
    import subprocess
    
    try:
        system = platform.system()
        
        if system == "Windows":
            cmd = ["tracert", "-h", "1", "127.0.0.1"]
        else:
            cmd = ["traceroute", "-m", "1", "127.0.0.1"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=10
        )
        
        return result.returncode == 0
        
    except Exception as e:
        logger.error(f"Traceroute capability check failed: {e}")
        return False


def get_firewall_suggestions() -> str:
    """
    Get platform-specific firewall configuration suggestions.
    
    Returns:
        Suggestions text
    """
    import platform
    
    system = platform.system()
    
    if system == "Windows":
        return """
Windows Firewall Configuration:
1. Open Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Allow Python through private and public networks
4. If using iperf3, allow port 5201

For traceroute to work, ICMP must be enabled (usually is by default).
"""
    elif system == "Linux":
        return """
Linux Firewall Configuration:
1. For traceroute: sudo apt-get install traceroute
2. For iperf3: sudo apt-get install iperf3
3. UFW firewall: sudo ufw allow 5201/tcp  # for iperf3
4. Run with sudo for raw socket access (traceroute)

Note: Some cloud providers block ICMP by default.
"""
    elif system == "Darwin":
        return """
macOS Firewall Configuration:
1. System Preferences > Security & Privacy > Firewall
2. Click "Firewall Options"
3. Allow Python and terminal to accept incoming connections
4. For iperf3: brew install iperf3

Note: May need to run with sudo for traceroute.
"""
    else:
        return "Platform-specific firewall suggestions not available."


def test_connectivity() -> dict:
    """
    Test network connectivity and capabilities.
    
    Returns:
        Dictionary with connectivity test results
    """
    results = {
        "internet": False,
        "nat": False,
        "local_ip": None,
        "external_ip": None,
        "traceroute": False,
        "iperf3_port": False,
        "suggestions": []
    }
    
    # Test internet connectivity
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        results["internet"] = True
    except:
        results["suggestions"].append("No internet connectivity detected")
    
    # Detect NAT
    is_nat, local_ip, external_ip = detect_nat()
    results["nat"] = is_nat
    results["local_ip"] = local_ip
    results["external_ip"] = external_ip
    
    if is_nat:
        results["suggestions"].append(
            "Behind NAT - other nodes will connect to your external IP. "
            "Make sure your router/firewall allows incoming connections for P2P."
        )
    
    # Check traceroute
    results["traceroute"] = check_traceroute_capability()
    if not results["traceroute"]:
        results["suggestions"].append(
            "Traceroute not working. May need elevated privileges (sudo/administrator). "
            "On Windows, run as Administrator. On Linux/Mac, use sudo."
        )
    
    # Check iperf3 port
    if results["external_ip"]:
        results["iperf3_port"] = check_port_open(results["external_ip"], 5201, timeout=2)
        if not results["iperf3_port"]:
            results["suggestions"].append(
                "iperf3 port (5201) not reachable. Bandwidth tests to this node may fail. "
                "Configure firewall/NAT to allow incoming TCP on port 5201."
            )
    
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Running connectivity tests...\n")
    results = test_connectivity()
    
    print("Results:")
    print(f"  Internet: {'✓' if results['internet'] else '✗'}")
    print(f"  Local IP: {results['local_ip']}")
    print(f"  External IP: {results['external_ip']}")
    print(f"  Behind NAT: {'Yes' if results['nat'] else 'No'}")
    print(f"  Traceroute: {'✓' if results['traceroute'] else '✗'}")
    print(f"  iperf3 port: {'✓' if results['iperf3_port'] else '✗'}")
    
    if results['suggestions']:
        print("\nSuggestions:")
        for suggestion in results['suggestions']:
            print(f"  • {suggestion}")
    
    print("\n" + get_firewall_suggestions())
