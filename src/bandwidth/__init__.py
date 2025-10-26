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
