"""
Intermap - Distributed P2P Internet Topology Mapper
Copyright (c) 2025 Jay Wenden
Licensed under CC-BY-NC-SA 4.0
"""
"""
API server for serving topology data to the frontend
"""
from flask import Flask, jsonify, send_file, send_from_directory, request
from flask_cors import CORS
from pathlib import Path
import logging
import json
from datetime import datetime
import socket
import sys
import threading

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.traceroute.tracer import Traceroute
from src.graph.gexf_generator import GEXFGenerator
from src.utils import is_public_ip

logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
FRONTEND_BUILD = PROJECT_ROOT / "frontend" / "build"
NODE_INFO_FILE = OUTPUT_DIR / "node_info.json"

# Initialize Flask with static folder pointing to frontend build
app = Flask(__name__, 
            static_folder=str(FRONTEND_BUILD / "static"),
            static_url_path='/static')
CORS(app)  # Enable CORS for frontend

# Store node's own external IP for highlighting in visualizer
OWN_EXTERNAL_IP = None

def load_node_info():
    """Load node info from file if available."""
    global OWN_EXTERNAL_IP
    try:
        if NODE_INFO_FILE.exists():
            with open(NODE_INFO_FILE, 'r') as f:
                info = json.load(f)
                OWN_EXTERNAL_IP = info.get('external_ip')
                logger.info(f"Loaded node info: {OWN_EXTERNAL_IP}")
    except Exception as e:
        logger.error(f"Failed to load node info: {e}")

def set_own_ip(ip: str):
    """Set the node's own external IP for visualization highlighting."""
    global OWN_EXTERNAL_IP
    OWN_EXTERNAL_IP = ip
    logger.info(f"API server tracking own IP: {ip}")


@app.route('/api/node/info', methods=['GET'])
def get_node_info():
    """Get information about this node (for highlighting in visualizer)."""
    try:
        # Reload from file in case it changed (mobile device)
        load_node_info()
        
        return jsonify({
            "external_ip": OWN_EXTERNAL_IP,
            "hostname": socket.gethostname(),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting node info: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/topology/latest', methods=['GET'])
def get_latest_topology():
    """Get the most recent GEXF topology file."""
    try:
        # Find most recent GEXF file
        gexf_files = sorted(OUTPUT_DIR.glob("topology_*.gexf"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not gexf_files:
            return jsonify({"error": "No topology data available yet"}), 404
        
        latest_file = gexf_files[0]
        
        return send_file(
            latest_file,
            mimetype='application/xml',
            as_attachment=False,
            download_name=latest_file.name
        )
        
    except Exception as e:
        logger.error(f"Error serving topology: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/topology/list', methods=['GET'])
def list_topologies():
    """List all available topology files."""
    try:
        gexf_files = sorted(OUTPUT_DIR.glob("topology_*.gexf"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        files = []
        for f in gexf_files:
            stat = f.stat()
            files.append({
                "filename": f.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "url": f"/api/topology/file/{f.name}"
            })
        
        return jsonify({"files": files})
        
    except Exception as e:
        logger.error(f"Error listing topologies: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/topology/file/<filename>', methods=['GET'])
def get_topology_file(filename):
    """Get a specific topology file by name."""
    try:
        file_path = OUTPUT_DIR / filename
        
        if not file_path.exists() or not file_path.is_file():
            return jsonify({"error": "File not found"}), 404
        
        # Security: ensure filename doesn't contain path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            return jsonify({"error": "Invalid filename"}), 400
        
        return send_file(
            file_path,
            mimetype='application/xml',
            as_attachment=False,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error serving file: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get network statistics."""
    try:
        # This could be enhanced to parse GEXF and return actual stats
        gexf_files = list(OUTPUT_DIR.glob("topology_*.gexf"))
        
        return jsonify({
            "topology_files": len(gexf_files),
            "last_update": datetime.now().isoformat(),
            "status": "active"
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/trace', methods=['POST'])
def trigger_traceroute():
    """
    Trigger a traceroute to a target IP or subnet.
    
    Request body:
    {
        "target": "8.8.8.8" or "192.168.1.0/24"
    }
    """
    try:
        data = request.get_json()
        if not data or 'target' not in data:
            return jsonify({"error": "Missing 'target' parameter"}), 400
        
        target = data['target'].strip()
        
        if not target:
            return jsonify({"error": "Target cannot be empty"}), 400
        
        # Check if target is a subnet or single IP
        if '/' in target:
            # Subnet traceroute
            return jsonify({"error": "Subnet tracing not yet implemented in API"}), 501
        else:
            # Single IP traceroute
            if not is_public_ip(target):
                return jsonify({"error": f"Target {target} is not a public IP address"}), 400
            
            # Run traceroute in background thread
            def run_trace():
                try:
                    logger.info(f"API: Starting traceroute to {target}")
                    tracer = Traceroute(max_hops=15, timeout=3, filter_private=False, verify_reachable=True)
                    hops = tracer.trace(target, filter_private_override=False)
                    
                    if hops:
                        logger.info(f"API: Traceroute to {target} completed with {len(hops)} hops")
                        
                        # Import NetworkGraph here to avoid circular imports
                        from src.graph.gexf_generator import NetworkGraph, GEXFGenerator
                        
                        # Load existing topology and merge
                        latest_file = OUTPUT_DIR / "topology_latest.gexf"
                        graph = NetworkGraph()
                        
                        if latest_file.exists():
                            try:
                                # Parse existing GEXF to preserve accumulated topology
                                import xml.etree.ElementTree as ET
                                tree = ET.parse(latest_file)
                                root = tree.getroot()
                                
                                # Define namespace
                                ns = {'gexf': 'http://gexf.net/1.3'}
                                
                                # Load existing nodes
                                for node in root.findall('.//gexf:node', ns):
                                    node_id = node.get('id')
                                    label = node.get('label', node_id)
                                    graph.add_node(node_id, hostname=label)
                                
                                # Load existing edges
                                for edge in root.findall('.//gexf:edge', ns):
                                    source = edge.get('source')
                                    target_node = edge.get('target')
                                    
                                    # Get RTT from edge attributes
                                    rtt_ms = None
                                    for attvalue in edge.findall('.//gexf:attvalue[@for="0"]', ns):
                                        try:
                                            rtt_ms = float(attvalue.get('value'))
                                        except (ValueError, TypeError):
                                            pass
                                    
                                    graph.add_edge(source, target_node, rtt_ms=rtt_ms)
                                
                                logger.info(f"API: Loaded existing topology: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
                            except Exception as e:
                                logger.warning(f"API: Could not load existing topology: {e}. Starting fresh.")
                        
                        # Add NEW traceroute hops to the existing graph
                        for hop in hops:
                            graph.add_node(hop.ip_address, hostname=hop.hostname)
                        
                        for i in range(len(hops) - 1):
                            graph.add_edge(
                                hops[i].ip_address,
                                hops[i+1].ip_address,
                                rtt_ms=abs(hops[i+1].rtt_ms - hops[i].rtt_ms)
                            )
                        
                        logger.info(f"API: Merged topology now has {len(graph.nodes)} nodes, {len(graph.edges)} edges")
                        
                        # Get external IP for adding as source node
                        from src.nat_detection import detect_nat_and_external_ip
                        try:
                            _, external_ip = detect_nat_and_external_ip()
                            if external_ip:
                                # Add YOUR NODE as the source of this traceroute
                                graph.add_node(external_ip, f"{external_ip} (YOU)")
                                
                                # Connect your node to first hop
                                if len(hops) > 0:
                                    first_hop = hops[0]
                                    graph.add_edge(
                                        external_ip,
                                        first_hop.ip_address,
                                        rtt_ms=first_hop.rtt_ms
                                    )
                                    logger.info(f"API: Added source node {external_ip} connected to first hop")
                        except Exception as e:
                            logger.warning(f"API: Could not add source node: {e}")
                        
                        # Generate timestamped backup
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        output_file = OUTPUT_DIR / f"topology_{timestamp}.gexf"
                        
                        generator = GEXFGenerator(graph)
                        generator.generate(str(output_file), title="Accumulated Internet Topology")
                        
                        # Update topology_latest.gexf with merged data
                        import shutil
                        shutil.copy(output_file, latest_file)
                        
                        logger.info(f"API: Updated topology file generated: {output_file}")
                    else:
                        logger.warning(f"API: Traceroute to {target} returned no hops")
                        
                except Exception as e:
                    logger.error(f"API: Traceroute thread error: {e}", exc_info=True)
            
            # Start background thread
            thread = threading.Thread(target=run_trace, daemon=True)
            thread.start()
            
            return jsonify({
                "status": "started",
                "target": target,
                "message": f"Traceroute to {target} started in background"
            }), 202
        
    except Exception as e:
        logger.error(f"Error triggering traceroute: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# Serve React frontend (production build)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve React frontend."""
    if FRONTEND_BUILD.exists():
        # For root path or empty path, serve index.html
        if not path:
            return send_from_directory(FRONTEND_BUILD, 'index.html')
        
        # Check if the requested file exists
        file_path = FRONTEND_BUILD / path
        
        if file_path.exists() and file_path.is_file():
            # Serve the specific file
            return send_from_directory(FRONTEND_BUILD, path)
        else:
            # For any missing file or path, serve index.html (SPA routing)
            return send_from_directory(FRONTEND_BUILD, 'index.html')
    else:
        return jsonify({
            "message": "Frontend not built. Run: cd frontend && npm run build",
            "api_endpoints": {
                "latest_topology": "/api/topology/latest",
                "list_topologies": "/api/topology/list",
                "stats": "/api/stats"
            }
        })


def run_server(host='0.0.0.0', port=5000):
    """Run the API server."""
    logger.info(f"Starting API server on {host}:{port}")
    try:
        logger.info(f"About to call app.run()...")
        app.run(host=host, port=port, debug=False, threaded=True, use_reloader=False)
        logger.info(f"app.run() returned (this should not happen!)")
    except Exception as e:
        logger.error(f"Exception during app.run(): {e}", exc_info=True)
        raise


if __name__ == "__main__":
    import os
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger.info("Starting API server as standalone module")
    
    # Use PORT environment variable if set (for Railway/Heroku), otherwise default to 5000
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Using port: {port}")
    run_server(port=port)

