import React, { useEffect, useRef } from 'react';
import { Network } from 'vis-network/standalone';

// Bandwidth color mapping (matches backend GEXF generator)
const BANDWIDTH_COLORS = {
  gigabit: '#00ff00',      // Green: >= 1000 Mbps
  fast: '#88ff00',         // Yellow-green: >= 100 Mbps
  medium: '#ffaa00',       // Orange: >= 10 Mbps
  slow: '#ff4400',         // Red-orange: >= 1 Mbps
  very_slow: '#ff0000',    // Red: < 1 Mbps
  unknown: '#888888'       // Gray: no bandwidth data
};

const getBandwidthColor = (bandwidth_mbps) => {
  if (!bandwidth_mbps) return BANDWIDTH_COLORS.unknown;
  if (bandwidth_mbps >= 1000) return BANDWIDTH_COLORS.gigabit;
  if (bandwidth_mbps >= 100) return BANDWIDTH_COLORS.fast;
  if (bandwidth_mbps >= 10) return BANDWIDTH_COLORS.medium;
  if (bandwidth_mbps >= 1) return BANDWIDTH_COLORS.slow;
  return BANDWIDTH_COLORS.very_slow;
};

const NetworkGraph = ({ data, ownNodeIp }) => {
  const containerRef = useRef(null);
  const networkRef = useRef(null);

  useEffect(() => {
    if (!data || !containerRef.current) return;

    // Prepare data for vis.js
    const nodes = data.nodes.map(node => {
      // Highlight user's own node in bright purple/magenta
      const isOwnNode = ownNodeIp && node.id === ownNodeIp;
      
      return {
        id: node.id,
        label: isOwnNode ? `⭐ ${node.label} (YOU)` : node.label,
        color: isOwnNode ? '#ff00ff' : (node.color || '#4488ff'), // Magenta for own node
        shape: 'dot',
        size: isOwnNode ? 30 : (node.type === 'participant' ? 20 : 15), // Larger for own node
        borderWidth: isOwnNode ? 4 : 2,
        font: isOwnNode ? { color: '#ffffff', size: 14, bold: true } : { color: '#ffffff', size: 12 },
      };
    });

    const edges = data.edges.map((edge, index) => {
      // Color edge based on bandwidth
      const bandwidth = edge.bandwidth_mbps;
      const color = getBandwidthColor(bandwidth);
      const width = bandwidth ? Math.min(Math.log10(bandwidth) + 1, 10) : 2;
      
      return {
        id: index,
        from: edge.from,
        to: edge.to,
        color: { color: color },
        width: width,
        title: bandwidth 
          ? `Bandwidth: ${bandwidth.toFixed(2)} Mbps\nLatency: ${edge.rtt_ms?.toFixed(2) || 'N/A'} ms`
          : `Latency: ${edge.rtt_ms?.toFixed(2) || 'N/A'} ms`,
      };
    });

    // Network options
    const options = {
      nodes: {
        font: {
          color: '#ffffff',
          size: 12,
        },
        borderWidth: 2,
        borderWidthSelected: 4,
      },
      edges: {
        smooth: {
          type: 'continuous',
        },
        arrows: {
          to: false,
        },
      },
      physics: {
        enabled: true,
        barnesHut: {
          gravitationalConstant: -2000,
          centralGravity: 0.3,
          springLength: 200,
          springConstant: 0.04,
          damping: 0.09,
        },
        stabilization: {
          iterations: 200,
        },
      },
      interaction: {
        hover: true,
        tooltipDelay: 100,
        navigationButtons: true,
        keyboard: true,
      },
    };

    // Create network
    const network = new Network(
      containerRef.current,
      { nodes, edges },
      options
    );

    networkRef.current = network;

    // Event handlers
    network.on('click', (params) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        console.log('Clicked node:', nodeId);
      }
    });

    // Cleanup
    return () => {
      if (networkRef.current) {
        networkRef.current.destroy();
      }
    };
  }, [data]);

  return (
    <div
      ref={containerRef}
      style={{
        width: '100%',
        height: '100%',
        backgroundColor: '#0a0a0a',
      }}
    />
  );
};

export default NetworkGraph;
