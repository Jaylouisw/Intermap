"""
Intermap - Distributed P2P Internet Topology Mapper
Copyright (c) 2025 Jay Wenden
Licensed under CC-BY-NC-SA 4.0
"""
"""
GEXF file generator for network topology visualization
"""
import logging
from typing import List, Dict
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
from xml.dom import minidom

logger = logging.getLogger(__name__)


class NetworkGraph:
    """
    Represents a network topology graph.
    
    Nodes represent hosts (routers, servers, endpoints).
    Edges represent network connections between hosts with RTT weights.
    """
    
    def __init__(self):
        self.nodes: Dict[str, Dict] = {}  # ip -> node data
        self.edges: Dict[tuple, Dict] = {}  # (source_ip, target_ip) -> edge data
        
    def add_node(self, ip_address: str, hostname: str = None, **attributes):
        """
        Add a node to the graph.
        
        Args:
            ip_address: IP address (node identifier)
            hostname: Optional hostname
            **attributes: Additional node attributes
        """
        if ip_address not in self.nodes:
            self.nodes[ip_address] = {
                "ip": ip_address,
                "hostname": hostname or ip_address,
                **attributes
            }
            logger.debug(f"Added node: {ip_address}")
    
    def add_edge(self, source_ip: str, target_ip: str, rtt_ms: float = None, bandwidth_mbps: float = None, bandwidth_upload_mbps: float = None, **attributes):
        """
        Add an edge between two nodes.
        
        Args:
            source_ip: Source node IP
            target_ip: Target node IP
            rtt_ms: Round-trip time in milliseconds (latency weight)
            bandwidth_mbps: Download bandwidth in Mbps (throughput)
            bandwidth_upload_mbps: Upload bandwidth in Mbps
            **attributes: Additional edge attributes
        """
        # Ensure nodes exist
        self.add_node(source_ip)
        self.add_node(target_ip)
        
        # Add edge with RTT and bandwidth (undirected - store in sorted order)
        edge_key = tuple(sorted([source_ip, target_ip]))
        
        edge_data = {
            "rtt_ms": rtt_ms,
            "bandwidth_mbps": bandwidth_mbps,
            "bandwidth_upload_mbps": bandwidth_upload_mbps,
            **attributes
        }
        
        # If edge exists, update with better metrics
        if edge_key in self.edges:
            existing_rtt = self.edges[edge_key].get("rtt_ms")
            if existing_rtt is None or (rtt_ms is not None and rtt_ms < existing_rtt):
                self.edges[edge_key]["rtt_ms"] = rtt_ms
            
            # Update download bandwidth (keep higher/peak value)
            existing_bw = self.edges[edge_key].get("bandwidth_mbps")
            if bandwidth_mbps is not None and (existing_bw is None or bandwidth_mbps > existing_bw):
                self.edges[edge_key]["bandwidth_mbps"] = bandwidth_mbps
            
            # Update upload bandwidth (keep higher/peak value)
            existing_up = self.edges[edge_key].get("bandwidth_upload_mbps")
            if bandwidth_upload_mbps is not None and (existing_up is None or bandwidth_upload_mbps > existing_up):
                self.edges[edge_key]["bandwidth_upload_mbps"] = bandwidth_upload_mbps
        else:
            self.edges[edge_key] = edge_data
            
            logger.debug(f"Added edge: {source_ip} <-> {target_ip} (RTT: {rtt_ms}ms, Down: {bandwidth_mbps}Mbps, Up: {bandwidth_upload_mbps}Mbps)")
    
    def remove_node(self, ip_address: str):
        """
        Remove a node and all its edges from the graph.
        
        Args:
            ip_address: IP address of the node to remove
        """
        if ip_address not in self.nodes:
            return
        
        # Remove node
        del self.nodes[ip_address]
        
        # Remove all edges connected to this node
        edges_to_remove = [
            edge_key for edge_key in self.edges.keys()
            if ip_address in edge_key
        ]
        
        for edge_key in edges_to_remove:
            del self.edges[edge_key]
        
        logger.debug(f"Removed node {ip_address} and {len(edges_to_remove)} edges")
    
    def merge_traceroute(self, traceroute_result: Dict):
        """
        Add traceroute results to the graph.
        
        Args:
            traceroute_result: Traceroute data containing hops
        """
        hops = traceroute_result.get("hops", [])
        
        # Add nodes for each hop
        for hop in hops:
            self.add_node(
                ip_address=hop["ip"],
                hostname=hop.get("hostname"),
                hop_number=hop["hop"],
                rtt=hop.get("rtt")
            )
        
        # Add edges between consecutive hops with RTT as weight
        for i in range(len(hops) - 1):
            current_hop = hops[i]
            next_hop = hops[i + 1]
            
            # Calculate RTT BETWEEN hops (segment latency)
            # Each hop's RTT is cumulative from source, so difference = segment time
            current_rtt = current_hop.get("rtt", 0)
            next_rtt = next_hop.get("rtt", 0)
            
            if current_rtt > 0 and next_rtt > 0:
                edge_rtt = abs(next_rtt - current_rtt)  # Absolute difference
            else:
                edge_rtt = None  # Unknown latency
                
            self.add_edge(
                current_hop["ip"], 
                next_hop["ip"],
                rtt_ms=edge_rtt
            )


class GEXFGenerator:
    """
    Generates GEXF (Graph Exchange XML Format) files from network topology data.
    
    GEXF is the native format for Gephi and supports rich graph visualization.
    Includes color coding based on bandwidth measurements.
    """
    
    # Bandwidth categories and colors (RGB hex) for modern multi-gigabit networking
    BANDWIDTH_COLORS = {
        "100gig": "00ffff",        # Cyan: >= 100 Gbps (datacenter)
        "40gig": "00ccff",         # Bright blue: >= 40 Gbps
        "25gig": "0099ff",         # Blue: >= 25 Gbps
        "10gig": "0066ff",         # Dark blue: >= 10 Gbps
        "5gig": "00ff00",          # Green: >= 5 Gbps
        "2.5gig": "66ff00",        # Lime green: >= 2.5 Gbps
        "gigabit": "aaff00",       # Yellow-green: >= 1 Gbps
        "fast": "ffdd00",          # Yellow: >= 100 Mbps
        "medium": "ffaa00",        # Orange: >= 10 Mbps
        "slow": "ff4400",          # Red-orange: >= 1 Mbps
        "very_slow": "ff0000",     # Red: < 1 Mbps
        "unknown": "888888"        # Gray: no bandwidth data
    }
    
    def __init__(self, graph: NetworkGraph):
        """
        Initialize GEXF generator with a network graph.
        
        Args:
            graph: NetworkGraph instance
        """
        self.graph = graph
    
    def _categorize_bandwidth(self, bandwidth_mbps: float = None) -> tuple:
        """
        Categorize bandwidth and return category name and color.
        
        Args:
            bandwidth_mbps: Bandwidth in Mbps
            
        Returns:
            Tuple of (category_name, color_hex)
        """
        if bandwidth_mbps is None:
            return ("unknown", self.BANDWIDTH_COLORS["unknown"])
        elif bandwidth_mbps >= 100000:  # >= 100 Gbps
            return ("100gig", self.BANDWIDTH_COLORS["100gig"])
        elif bandwidth_mbps >= 40000:   # >= 40 Gbps
            return ("40gig", self.BANDWIDTH_COLORS["40gig"])
        elif bandwidth_mbps >= 25000:   # >= 25 Gbps
            return ("25gig", self.BANDWIDTH_COLORS["25gig"])
        elif bandwidth_mbps >= 10000:   # >= 10 Gbps
            return ("10gig", self.BANDWIDTH_COLORS["10gig"])
        elif bandwidth_mbps >= 5000:    # >= 5 Gbps
            return ("5gig", self.BANDWIDTH_COLORS["5gig"])
        elif bandwidth_mbps >= 2500:    # >= 2.5 Gbps
            return ("2.5gig", self.BANDWIDTH_COLORS["2.5gig"])
        elif bandwidth_mbps >= 1000:    # >= 1 Gbps
            return ("gigabit", self.BANDWIDTH_COLORS["gigabit"])
        elif bandwidth_mbps >= 100:
            return ("fast", self.BANDWIDTH_COLORS["fast"])
        elif bandwidth_mbps >= 10:
            return ("medium", self.BANDWIDTH_COLORS["medium"])
        elif bandwidth_mbps >= 1:
            return ("slow", self.BANDWIDTH_COLORS["slow"])
        else:
            return ("very_slow", self.BANDWIDTH_COLORS["very_slow"])
    
    def generate(self, filepath: str, title: str = "Internet Topology Map"):
        """
        Generate GEXF file from the network graph.
        
        Args:
            filepath: Output file path
            title: Graph title/description
        """
        logger.info(f"Generating GEXF file: {filepath}")
        
        # Create root GEXF element
        gexf = Element("gexf")
        gexf.set("xmlns", "http://gexf.net/1.3")
        gexf.set("version", "1.3")
        
        # Add metadata
        meta = SubElement(gexf, "meta")
        meta.set("lastmodifieddate", datetime.now().isoformat())
        creator = SubElement(meta, "creator")
        creator.text = "Distributed Internet Topology Mapper"
        description = SubElement(meta, "description")
        description.text = title
        
        # Create graph element
        graph_elem = SubElement(gexf, "graph")
        graph_elem.set("mode", "static")
        graph_elem.set("defaultedgetype", "undirected")
        
        # Add node attributes definitions
        node_attributes = SubElement(graph_elem, "attributes")
        node_attributes.set("class", "node")
        
        attr_hostname = SubElement(node_attributes, "attribute")
        attr_hostname.set("id", "0")
        attr_hostname.set("title", "hostname")
        attr_hostname.set("type", "string")
        
        # Add edge attributes definitions (for RTT and bandwidth)
        edge_attributes = SubElement(graph_elem, "attributes")
        edge_attributes.set("class", "edge")
        
        attr_rtt = SubElement(edge_attributes, "attribute")
        attr_rtt.set("id", "0")
        attr_rtt.set("title", "rtt_ms")
        attr_rtt.set("type", "float")
        
        attr_bandwidth = SubElement(edge_attributes, "attribute")
        attr_bandwidth.set("id", "1")
        attr_bandwidth.set("title", "bandwidth_download_mbps")
        attr_bandwidth.set("type", "float")
        
        attr_bandwidth_up = SubElement(edge_attributes, "attribute")
        attr_bandwidth_up.set("id", "2")
        attr_bandwidth_up.set("title", "bandwidth_upload_mbps")
        attr_bandwidth_up.set("type", "float")
        
        attr_color = SubElement(edge_attributes, "attribute")
        attr_color.set("id", "3")
        attr_color.set("title", "speed_category")
        attr_color.set("type", "string")
        
        # Add nodes
        nodes_elem = SubElement(graph_elem, "nodes")
        for node_id, node_data in self.graph.nodes.items():
            node = SubElement(nodes_elem, "node")
            node.set("id", node_id)
            node.set("label", node_data.get("hostname", node_id))
            
            # Add node attributes
            attvalues = SubElement(node, "attvalues")
            attvalue = SubElement(attvalues, "attvalue")
            attvalue.set("for", "0")
            attvalue.set("value", node_data.get("hostname", node_id))
        
        # Add edges with RTT and bandwidth
        edges_elem = SubElement(graph_elem, "edges")
        for edge_id, (edge_key, edge_data) in enumerate(self.graph.edges.items()):
            source, target = edge_key
            edge = SubElement(edges_elem, "edge")
            edge.set("id", str(edge_id))
            edge.set("source", source)
            edge.set("target", target)
            
            # Get edge metrics
            rtt_ms = edge_data.get("rtt_ms")
            bandwidth_mbps = edge_data.get("bandwidth_mbps")
            bandwidth_upload_mbps = edge_data.get("bandwidth_upload_mbps")
            
            # Determine speed category and color based on bandwidth
            speed_category, color = self._categorize_bandwidth(bandwidth_mbps)
            
            # Set edge LENGTH based on RTT (lower RTT = shorter edge for better visualization)
            # Use RTT as length directly - visualization tools will interpret this
            if rtt_ms is not None:
                edge.set("length", str(rtt_ms))
            
            # Set weight (use bandwidth if available, otherwise inverse RTT)
            if bandwidth_mbps is not None:
                edge.set("weight", str(bandwidth_mbps))
            elif rtt_ms is not None:
                edge.set("weight", str(1000 / rtt_ms))  # Inverse RTT as weight
            
            # Set edge color based on bandwidth
            if color:
                edge.set("color", color)
            
            # Add as attribute values
            edge_attvalues = SubElement(edge, "attvalues")
            
            if rtt_ms is not None:
                rtt_attvalue = SubElement(edge_attvalues, "attvalue")
                rtt_attvalue.set("for", "0")
                rtt_attvalue.set("value", str(rtt_ms))
            
            if bandwidth_mbps is not None:
                bw_attvalue = SubElement(edge_attvalues, "attvalue")
                bw_attvalue.set("for", "1")
                bw_attvalue.set("value", str(bandwidth_mbps))
            
            if bandwidth_upload_mbps is not None:
                bw_up_attvalue = SubElement(edge_attvalues, "attvalue")
                bw_up_attvalue.set("for", "2")
                bw_up_attvalue.set("value", str(bandwidth_upload_mbps))
            
            if speed_category:
                cat_attvalue = SubElement(edge_attvalues, "attvalue")
                cat_attvalue.set("for", "3")
                cat_attvalue.set("value", speed_category)
        
        # Write to file with pretty printing
        xml_str = minidom.parseString(tostring(gexf)).toprettyxml(indent="  ")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(xml_str)
        
        logger.info(f"GEXF file generated: {len(self.graph.nodes)} nodes, {len(self.graph.edges)} edges")
    
    def to_string(self) -> str:
        """Generate GEXF as string instead of file."""
        # TODO: Implement string generation
        return ""


def create_gexf_from_traceroutes(traceroute_results: List[Dict], output_path: str):
    """
    Convenience function to create GEXF from multiple traceroute results.
    
    Args:
        traceroute_results: List of traceroute result dictionaries
        output_path: Output file path
    """
    graph = NetworkGraph()
    
    for result in traceroute_results:
        graph.merge_traceroute(result)
    
    generator = GEXFGenerator(graph)
    generator.generate(output_path)


if __name__ == "__main__":
    # Test GEXF generation
    logging.basicConfig(level=logging.INFO)
    
    # Create sample graph
    graph = NetworkGraph()
    graph.add_node("192.168.1.1", hostname="router.local")
    graph.add_node("8.8.8.8", hostname="dns.google")
    graph.add_edge("192.168.1.1", "8.8.8.8")
    
    # Generate GEXF
    generator = GEXFGenerator(graph)
    generator.generate("test_topology.gexf", "Test Network")
    print("Generated test_topology.gexf")
