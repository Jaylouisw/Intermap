"""
Intermap - Distributed P2P Internet Topology Mapper
Copyright (c) 2025 Jay Wenden
Licensed under CC-BY-NC-SA 4.0

Dynamic iperf3 server list fetcher from GitHub repository.
"""
import re
import logging
import requests
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

GITHUB_README_URL = "https://raw.githubusercontent.com/R0GGER/public-iperf3-servers/main/README.md"


def parse_iperf3_command(command: str) -> Optional[Dict[str, any]]:
    """
    Parse iperf3 command string to extract host and port.
    
    Examples:
        "iperf3 -c ping.online.net -p 5200-5209" -> {"host": "ping.online.net", "port": 5200}
        "iperf3 -c 8.8.8.8" -> {"host": "8.8.8.8", "port": 5201}
    
    Args:
        command: iperf3 command string from README
        
    Returns:
        Dict with host and port, or None if parsing fails
    """
    # Extract hostname/IP after "-c "
    host_match = re.search(r'-c\s+([^\s]+)', command)
    if not host_match:
        return None
    
    host = host_match.group(1)
    
    # Extract port after "-p " (if present)
    port_match = re.search(r'-p\s+(\d+)', command)
    if port_match:
        port = int(port_match.group(1))
    else:
        port = 5201  # Default iperf3 port
    
    return {"host": host, "port": port}


def fetch_iperf3_servers(timeout: int = 10) -> List[Dict[str, any]]:
    """
    Fetch all iperf3 servers from the GitHub README.
    
    Args:
        timeout: HTTP request timeout in seconds
        
    Returns:
        List of dicts with keys: host, port, location, continent
    """
    try:
        logger.info(f"Fetching iperf3 servers from: {GITHUB_README_URL}")
        response = requests.get(GITHUB_README_URL, timeout=timeout)
        response.raise_for_status()
        
        content = response.text
        servers = []
        current_continent = None
        
        for line in content.split('\n'):
            # Detect continent headers
            if line.startswith('### '):
                current_continent = line.replace('### ', '').strip()
                continue
            
            # Parse server lines (format: | iperf3 -c ... | options | speed | country | site |)
            if line.startswith('| iperf3 -c '):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 5:
                    command = parts[1]
                    country = parts[4] if len(parts) > 4 else "Unknown"
                    site = parts[5] if len(parts) > 5 else "Unknown"
                    
                    # Parse command
                    server_info = parse_iperf3_command(command)
                    if server_info:
                        server_info['location'] = site
                        server_info['continent'] = current_continent or "Unknown"
                        server_info['country'] = country
                        servers.append(server_info)
        
        logger.info(f"Successfully parsed {len(servers)} iperf3 servers")
        return servers
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch iperf3 servers: {e}")
        return []
    except Exception as e:
        logger.error(f"Error parsing iperf3 servers: {e}")
        return []


def get_server_hosts(max_servers: Optional[int] = None) -> List[str]:
    """
    Get list of iperf3 server hostnames/IPs.
    
    Args:
        max_servers: Maximum number of servers to return (None = all)
        
    Returns:
        List of hostname/IP strings
    """
    servers = fetch_iperf3_servers()
    hosts = [s['host'] for s in servers]
    
    if max_servers:
        hosts = hosts[:max_servers]
    
    return hosts


def get_geographically_diverse_servers(count: int = 20) -> List[Dict[str, any]]:
    """
    Get a geographically diverse subset of iperf3 servers.
    Distributes across continents evenly.
    
    Args:
        count: Number of servers to return
        
    Returns:
        List of server dicts
    """
    all_servers = fetch_iperf3_servers()
    
    if not all_servers:
        return []
    
    # Group by continent
    by_continent = {}
    for server in all_servers:
        continent = server.get('continent', 'Unknown')
        if continent not in by_continent:
            by_continent[continent] = []
        by_continent[continent].append(server)
    
    # Select evenly from each continent
    selected = []
    per_continent = max(1, count // len(by_continent))
    
    for continent, servers in by_continent.items():
        selected.extend(servers[:per_continent])
    
    # Fill remaining slots if needed
    if len(selected) < count:
        remaining = count - len(selected)
        for server in all_servers:
            if server not in selected:
                selected.append(server)
                remaining -= 1
                if remaining == 0:
                    break
    
    logger.info(f"Selected {len(selected)} geographically diverse servers")
    return selected[:count]


if __name__ == "__main__":
    # Test the parser
    logging.basicConfig(level=logging.INFO)
    
    test_commands = [
        "iperf3 -c ping.online.net -p 5200-5209",
        "iperf3 -c 8.8.8.8",
        "iperf3 -c speedtest.wtnet.de",
    ]
    
    print("Testing parser:")
    for cmd in test_commands:
        result = parse_iperf3_command(cmd)
        print(f"  {cmd} -> {result}")
    
    print("\nFetching all servers...")
    servers = fetch_iperf3_servers()
    print(f"Found {len(servers)} servers")
    
    print("\nFirst 5 servers:")
    for server in servers[:5]:
        print(f"  {server}")
    
    print("\nGeographically diverse selection (10 servers):")
    diverse = get_geographically_diverse_servers(10)
    for server in diverse:
        print(f"  {server['host']} ({server['location']}, {server['continent']})")
