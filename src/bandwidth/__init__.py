"""
Intermap - Distributed P2P Internet Topology Mapper
Copyright (c) 2025 Jay Wenden
Licensed under CC-BY-NC-SA 4.0
"""
"""
Bandwidth testing module
"""
from .bandwidth_tester import (
    IPerf3Client,
    SpeedtestClient,
    BandwidthResult,
    PUBLIC_IPERF3_SERVERS,
    test_public_servers
)

__all__ = [
    'IPerf3Client',
    'SpeedtestClient',
    'BandwidthResult',
    'PUBLIC_IPERF3_SERVERS',
    'test_public_servers'
]
