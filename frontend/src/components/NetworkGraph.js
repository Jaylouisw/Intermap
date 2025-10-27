/**
 * Intermap - Distributed P2P Internet Topology Mapper
 * Copyright (c) 2025 Jay Wenden
 * Licensed under CC-BY-NC-SA 4.0
 */

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

    // Calculate network hierarchy (distance from your node) - Zenmap style
    const calculateHierarchy = () => {
      const distances = {};
      const visited = new Set();
      const queue = [];
      
      // Find your node or use first node as center
      const centerNode = ownNodeIp || data.nodes[0]?.id;
      
      console.log('Center node:', centerNode);
      console.log('Own node IP:', ownNodeIp);
      console.log('First node:', data.nodes[0]?.id);
      console.log('All node IDs:', data.nodes.map(n => n.id).slice(0, 10));
      
      if (!centerNode) return distances;
      
      // BFS to calculate distances
      distances[centerNode] = 0;
      queue.push(centerNode);
      visited.add(centerNode);
      
      let edgeCount = 0;
      while (queue.length > 0) {
        const current = queue.shift();
        const currentDist = distances[current];
        
        // Find all connected nodes
        data.edges.forEach(edge => {
          let neighbor = null;
          if (edge.from === current && !visited.has(edge.to)) {
            neighbor = edge.to;
            edgeCount++;
          } else if (edge.to === current && !visited.has(edge.from)) {
            neighbor = edge.from;
            edgeCount++;
          }
          
          if (neighbor) {
            distances[neighbor] = currentDist + 1;
            visited.add(neighbor);
            queue.push(neighbor);
          }
        });
      }
      
      console.log('Hierarchy calculated:', distances);
      console.log('Edges processed:', edgeCount);
      console.log('Distance breakdown:', Object.values(distances).reduce((acc, dist) => {
        acc[dist] = (acc[dist] || 0) + 1;
        return acc;
      }, {}));
      
      return distances;
    };
    
    const hierarchy = calculateHierarchy();
    const maxLevel = Math.max(...Object.values(hierarchy), 0);
    
    // Pre-calculate radial positions for true Zenmap ring layout
    const nodesByLevel = {};
    data.nodes.forEach(node => {
      const level = hierarchy[node.id] || maxLevel + 1;
      if (!nodesByLevel[level]) nodesByLevel[level] = [];
      nodesByLevel[level].push(node);
    });
    
    // Assign radial positions (rings)
    const nodePositions = {};
    Object.keys(nodesByLevel).forEach(level => {
      const nodes = nodesByLevel[level];
      const radius = parseInt(level) * 250; // 250px per hop level
      const angleStep = (2 * Math.PI) / nodes.length;
      
      nodes.forEach((node, index) => {
        const angle = index * angleStep;
        nodePositions[node.id] = {
          x: radius * Math.cos(angle),
          y: radius * Math.sin(angle),
        };
      });
    });
    
    // Prepare data for vis.js with Zenmap-style radial layout
    const nodes = data.nodes.map(node => {
      const isOwnNode = ownNodeIp && node.id === ownNodeIp;
      const level = hierarchy[node.id] || maxLevel + 1;
      const position = nodePositions[node.id] || { x: 0, y: 0 };
      
      // Color nodes based on network distance (Zenmap style)
      let nodeColor = '#4488ff'; // Default blue
      if (isOwnNode) {
        nodeColor = '#00ff00'; // Green for your node (Zenmap center)
      } else if (level === 1) {
        nodeColor = '#ffff00'; // Yellow for direct neighbors
      } else if (level === 2) {
        nodeColor = '#ff8800'; // Orange for 2 hops away
      } else if (level >= 3) {
        nodeColor = '#ff4444'; // Red for distant nodes
      }
      
      return {
        id: node.id,
        label: isOwnNode ? `${node.label}\n(YOU)` : node.label,
        color: {
          background: nodeColor,
          border: isOwnNode ? '#00ff00' : '#ffffff',
          highlight: {
            background: nodeColor,
            border: '#00ffff',
          },
        },
        shape: isOwnNode ? 'star' : 'dot', // Star for your node like Zenmap
        size: isOwnNode ? 35 : Math.max(25 - (level * 2), 12), // Larger = closer
        borderWidth: isOwnNode ? 4 : 2,
        font: { 
          color: '#ffffff', 
          size: isOwnNode ? 14 : 11,
          bold: isOwnNode,
        },
        level: level,
        x: position.x, // Pre-calculated radial position
        y: position.y,
        fixed: isOwnNode ? { x: true, y: true } : false, // Only fix your node
        title: `${node.label}\nDistance: ${level} hop${level !== 1 ? 's' : ''}`,
      };
    });

    const edges = data.edges.map((edge, index) => {
      const bandwidth = edge.bandwidth_mbps;
      const color = getBandwidthColor(bandwidth);
      const width = bandwidth ? Math.min(Math.log10(bandwidth) + 1, 10) : 2;
      
      return {
        id: index,
        from: edge.from,
        to: edge.to,
        color: { 
          color: color,
          opacity: 0.6,
        },
        width: width,
        smooth: {
          type: 'curvedCW',
          roundness: 0.2,
        },
        title: bandwidth 
          ? `Bandwidth: ${bandwidth.toFixed(2)} Mbps\nLatency: ${edge.rtt_ms?.toFixed(2) || 'N/A'} ms`
          : `Latency: ${edge.rtt_ms?.toFixed(2) || 'N/A'} ms`,
      };
    });

    // Zenmap-style radial layout with manual positioning
    const options = {
      layout: {
        randomSeed: 42, // Consistent layout
      },
      nodes: {
        font: {
          color: '#ffffff',
          size: 12,
        },
        borderWidth: 2,
        borderWidthSelected: 4,
        shadow: false, // Disable shadows for performance
      },
      edges: {
        smooth: {
          enabled: true,
          type: 'continuous', // Simpler smooth type for performance
        },
        arrows: {
          to: {
            enabled: false,
          },
        },
        shadow: false, // Disable shadows for performance
      },
      physics: {
        enabled: true,
        stabilization: {
          enabled: true,
          iterations: 50, // Very few iterations since we pre-positioned
          updateInterval: 10,
        },
        barnesHut: {
          gravitationalConstant: -1000, // Weak gravity, just for minor adjustments
          centralGravity: 0.01,
          springLength: 250,
          springConstant: 0.0005, // Very weak springs
          damping: 0.9, // Heavy damping for quick stabilization
          avoidOverlap: 1.0,
        },
        minVelocity: 1.0, // Stop physics quickly
        solver: 'barnesHut',
        timestep: 0.35,
      },
      interaction: {
        hover: true,
        tooltipDelay: 200,
        navigationButtons: true,
        keyboard: true,
        zoomView: true,
        dragView: true,
        hideEdgesOnDrag: true, // Hide edges while dragging for performance
        hideEdgesOnZoom: false,
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
