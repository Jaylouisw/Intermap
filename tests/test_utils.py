"""
Unit tests for utility functions
"""
import pytest
from src.utils import is_valid_ip, format_rtt


def test_is_valid_ip_valid():
    """Test IP validation with valid IPs."""
    assert is_valid_ip("192.168.1.1") == True
    assert is_valid_ip("8.8.8.8") == True
    assert is_valid_ip("127.0.0.1") == True


def test_is_valid_ip_invalid():
    """Test IP validation with invalid IPs."""
    assert is_valid_ip("not.an.ip") == False
    assert is_valid_ip("999.999.999.999") == False
    assert is_valid_ip("") == False


def test_format_rtt():
    """Test RTT formatting."""
    assert format_rtt(1.234) == "1.23 ms"
    assert format_rtt(10.5) == "10.50 ms"
    assert format_rtt(0.1) == "0.10 ms"
