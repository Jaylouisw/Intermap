"""
Intermap - Distributed P2P Internet Topology Mapper
Copyright (c) 2025 Jay Wenden
Licensed under CC-BY-NC-SA 4.0
"""
"""
Unit tests for GEXF graph generation
"""
import pytest
import tempfile
import os
from src.graph.gexf_generator import NetworkGraph, GEXFGenerator


def test_network_graph_add_node():
    """Test adding nodes to the graph."""
    graph = NetworkGraph()
    graph.add_node("192.168.1.1", hostname="router")
    
    assert "192.168.1.1" in graph.nodes
    assert graph.nodes["192.168.1.1"]["hostname"] == "router"


def test_network_graph_add_edge():
    """Test adding edges to the graph."""
    graph = NetworkGraph()
    graph.add_edge("192.168.1.1", "8.8.8.8")
    
    assert len(graph.edges) == 1
    assert ("192.168.1.1", "8.8.8.8") in graph.edges or ("8.8.8.8", "192.168.1.1") in graph.edges


def test_gexf_generation():
    """Test GEXF file generation."""
    graph = NetworkGraph()
    graph.add_node("192.168.1.1", hostname="router")
    graph.add_node("8.8.8.8", hostname="google")
    graph.add_edge("192.168.1.1", "8.8.8.8")
    
    # Generate GEXF to temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.gexf') as f:
        temp_path = f.name
    
    try:
        generator = GEXFGenerator(graph)
        generator.generate(temp_path)
        
        # Verify file was created
        assert os.path.exists(temp_path)
        
        # Verify file contains expected content
        with open(temp_path, 'r') as f:
            content = f.read()
            assert 'gexf' in content
            assert '192.168.1.1' in content
            assert '8.8.8.8' in content
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# TODO: Add tests for merge_traceroute functionality
