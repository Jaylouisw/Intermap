"""
Unit tests for traceroute functionality
"""
import pytest
from src.traceroute.tracer import Traceroute, Hop, trace_to_target


def test_traceroute_initialization():
    """Test traceroute object initialization."""
    tracer = Traceroute(max_hops=20, timeout=3)
    assert tracer.max_hops == 20
    assert tracer.timeout == 3


def test_hop_dataclass():
    """Test Hop dataclass creation."""
    hop = Hop(
        hop_number=1,
        ip_address="192.168.1.1",
        hostname="router.local",
        rtt_ms=1.23
    )
    assert hop.hop_number == 1
    assert hop.ip_address == "192.168.1.1"
    assert hop.hostname == "router.local"
    assert hop.rtt_ms == 1.23


# TODO: Add more tests for actual traceroute functionality
# TODO: Add mock tests for system commands
