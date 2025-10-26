"""
Intermap - Distributed P2P Internet Topology Mapper
Copyright (c) 2025 Jay Wenden
Licensed under CC-BY-NC-SA 4.0
"""
"""
Test configuration for pytest
"""
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
