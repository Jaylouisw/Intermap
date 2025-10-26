"""
Utility functions and helpers
"""
import logging
from typing import Optional, List
import socket
import ipaddress

logger = logging.getLogger(__name__)


def is_valid_ip(ip_string: str) -> bool:
    """
    Check if a string is a valid IP address.
    
    Args:
        ip_string: String to validate
        
    Returns:
        True if valid IP address, False otherwise
    """
    try:
        socket.inet_aton(ip_string)
        return True
    except socket.error:
        return False


def is_private_ip(ip_string: str) -> bool:
    """
    Check if an IP address is private (RFC1918, loopback, link-local, etc.).
    
    SECURITY: Private IPs must NEVER be included in public topology data.
    
    Args:
        ip_string: IP address to check
        
    Returns:
        True if private/internal IP, False if public
    """
    try:
        ip_obj = ipaddress.ip_address(ip_string)
        return ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved
    except ValueError:
        logger.warning(f"Invalid IP address: {ip_string}")
        return True  # Treat invalid IPs as private for safety


def is_public_ip(ip_string: str) -> bool:
    """
    Check if an IP address is public (routable on the internet).
    
    Args:
        ip_string: IP address to check
        
    Returns:
        True if public IP, False if private/internal
    """
    return not is_private_ip(ip_string)


def filter_private_ips(ip_list: List[str]) -> List[str]:
    """
    Filter out private IP addresses from a list.
    
    Args:
        ip_list: List of IP addresses
        
    Returns:
        List containing only public IP addresses
    """
    return [ip for ip in ip_list if is_public_ip(ip)]


def expand_subnet(subnet: str) -> List[str]:
    """
    Expand a subnet into a list of individual IP addresses.
    
    Args:
        subnet: Subnet in CIDR notation (e.g., "8.8.8.0/24")
        
    Returns:
        List of IP addresses in the subnet
    """
    try:
        network = ipaddress.ip_network(subnet, strict=False)
        
        # Limit subnet size to prevent abuse
        if network.num_addresses > 256:
            logger.warning(f"Subnet too large ({network.num_addresses} addresses), limiting to /24")
            return []
        
        return [str(ip) for ip in network.hosts()]
    except ValueError as e:
        logger.error(f"Invalid subnet: {subnet} - {e}")
        return []


def resolve_hostname(hostname: str) -> Optional[str]:
    """
    Resolve a hostname to an IP address.
    
    Args:
        hostname: Hostname to resolve
        
    Returns:
        IP address string, or None if resolution fails
    """
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        logger.warning(f"Failed to resolve hostname: {hostname}")
        return None


def get_hostname(ip_address: str) -> Optional[str]:
    """
    Perform reverse DNS lookup for an IP address.
    
    Args:
        ip_address: IP address to lookup
        
    Returns:
        Hostname string, or None if lookup fails
    """
    try:
        return socket.gethostbyaddr(ip_address)[0]
    except socket.herror:
        return None


def format_rtt(rtt_ms: float) -> str:
    """
    Format round-trip time for display.
    
    Args:
        rtt_ms: RTT in milliseconds
        
    Returns:
        Formatted string (e.g., "1.23 ms")
    """
    return f"{rtt_ms:.2f} ms"
