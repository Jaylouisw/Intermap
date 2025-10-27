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

    const nodeCount = data.nodes.length;
    const enableClustering = nodeCount > 100; // Enable clustering for large graphs
    
    console.log(`Network has ${nodeCount} nodes. Clustering: ${enableClustering ? 'enabled' : 'disabled'}`);

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
  const maxLevel = Object.keys(hierarchy).length ? Math.max(...Object.values(hierarchy)) : 0;
    
    // Pre-calculate radial positions for true Zenmap ring layout
    const nodesByLevel = {};
    data.nodes.forEach(node => {
      const level = hierarchy[node.id] || maxLevel + 1;
      if (!nodesByLevel[level]) nodesByLevel[level] = [];
      nodesByLevel[level].push(node);
    });
    
    // Assign radial positions (rings) — deterministic concentric rings like Zenmap
    const nodePositions = {};
    const baseRadius = 150; // Zenmap-style compact rings
    Object.keys(nodesByLevel).forEach(levelKey => {
      const level = parseInt(levelKey, 10);
      const nodes = nodesByLevel[levelKey];
      const radius = level === 0 ? 0 : level * baseRadius; // center node at origin
      const angleStep = (2 * Math.PI) / Math.max(nodes.length, 1);

      nodes.forEach((node, index) => {
        if (level === 0) {
          // Center node at origin
          nodePositions[node.id] = { x: 0, y: 0 };
        } else {
          const angle = index * angleStep - Math.PI / 2; // start from top
          nodePositions[node.id] = {
            x: Math.round(radius * Math.cos(angle)),
            y: Math.round(radius * Math.sin(angle)),
          };
        }
      });
    });
    
    // Prepare data for vis.js with Zenmap-style radial layout
    // Determine node types and colors. If the node has attributes.type use it, otherwise heuristics
    const TYPE_COLORS = {
      participant: '#00ff00',  // Bright green (Zenmap center node style)
      iperf: '#9370db',        // Medium purple
      dns: '#00bfff',          // Deep sky blue
      router: '#ffa500',       // Orange
      switch: '#a9a9a9',       // Dark gray
      unknown: '#4169e1',      // Royal blue
    };

    const isPrivateIP = (ip) => {
      if (!ip) return false;
      // Basic IPv4 private checks
      return /^10\.|^192\.168\.|^172\.(1[6-9]|2[0-9]|3[0-1])\./.test(ip);
    };

    const nodes = data.nodes.map(node => {
      const isOwnNode = ownNodeIp && node.id === ownNodeIp;
      const level = hierarchy[node.id] || maxLevel + 1;
      const position = nodePositions[node.id] || { x: 0, y: 0 };

      const attrs = node.attributes || {};
      // prefer explicit type attribute if present
      let type = (attrs.type && String(attrs.type).toLowerCase()) || null;

      if (!type) {
        // heuristics
        const id = String(node.id || '').toLowerCase();
        const label = String(node.label || '').toLowerCase();
        if (id === ownNodeIp || label.includes('you')) type = 'participant';
        else if (label.includes('iperf') || label.includes('speedtest')) type = 'iperf';
        else if (['1.1.1.1', '8.8.8.8', '8.8.4.4', '9.9.9.9', '208.67.222.222', '208.67.220.220'].includes(id)) type = 'dns';
        else if (isPrivateIP(id)) type = 'switch';
        else type = 'router';
      }

      const nodeColor = TYPE_COLORS[type] || TYPE_COLORS.unknown;

      return {
        id: node.id,
        label: isOwnNode ? `${node.label}\n(YOU)` : node.label,
        color: {
          background: isOwnNode ? '#00ff00' : nodeColor,
          border: isOwnNode ? '#00ff00' : '#ffffff',
          highlight: {
            background: isOwnNode ? '#66ff66' : nodeColor,
            border: '#ffff00', // Yellow highlight border (Zenmap style)
          },
        },
        shape: isOwnNode ? 'star' : 'dot',
        size: isOwnNode ? 30 : Math.max(20 - (level * 1.2), 8), // Zenmap-style sizing
        borderWidth: isOwnNode ? 3 : 1.5,
        font: {
          color: '#ffffff',
          size: isOwnNode ? 13 : 9,
          bold: isOwnNode,
          face: 'arial',
        },
        level: level,
        x: position.x,
        y: position.y,
        fixed: { x: true, y: true }, // fix every node to the precomputed position for stable rings
        title: `${node.label}\nType: ${type}\nDistance: ${level} hop${level !== 1 ? 's' : ''}`,
      };
    });

    const edges = data.edges.map((edge, index) => {
      const bandwidth = edge.bandwidth_download_mbps || edge.bandwidth_mbps || null;
      const color = getBandwidthColor(bandwidth);
      const width = bandwidth ? Math.min(Math.log10(bandwidth) + 1, 6) : 1; // Thinner edges for Zenmap look

      const titleLines = [];
      if (edge.rtt_ms != null) titleLines.push(`RTT: ${Number(edge.rtt_ms).toFixed(2)} ms`);
      if (edge.bandwidth_download_mbps != null) titleLines.push(`DL: ${Number(edge.bandwidth_download_mbps).toFixed(2)} Mbps`);
      if (edge.bandwidth_upload_mbps != null) titleLines.push(`UL: ${Number(edge.bandwidth_upload_mbps).toFixed(2)} Mbps`);
      const title = titleLines.length ? titleLines.join('\n') : 'No metrics available';

      return {
        id: index,
        from: edge.from,
        to: edge.to,
        color: {
          color: color,
          opacity: 0.6, // Semi-transparent like Zenmap
        },
        width: width,
        smooth: {
          type: 'continuous', // Straight lines like Zenmap
          enabled: false,
        },
        title,
      };
    });

    // Zenmap-style radial layout with manual positioning (physics disabled for smooth pan/zoom)
    const options = {
      layout: {
        randomSeed: 42, // Consistent layout
      },
      nodes: {
        font: {
          color: '#ffffff',
          size: 10,
          face: 'arial',
        },
        borderWidth: 1.5,
        borderWidthSelected: 3,
        shadow: false, // Disable shadows for performance
      },
      edges: {
        smooth: {
          enabled: false, // Straight lines for performance and Zenmap look
        },
        arrows: {
          to: {
            enabled: false,
          },
        },
        shadow: false, // Disable shadows for performance
      },
      physics: {
        enabled: false, // disable physics entirely because we pre-position nodes on rings
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

    // Enable clustering for large graphs (>100 nodes)
    if (enableClustering) {
      console.log('Enabling clustering for large topology...');
      
      // Cluster distant nodes (level 3+) for performance
      const clusterByLevel = (level) => {
        const clusterOptionsByLevel = {
          processProperties: (clusterOptions, childNodes, childEdges) => {
            let totalMass = 0;
            for (let i = 0; i < childNodes.length; i++) {
              totalMass += childNodes[i].mass || 1;
            }
            clusterOptions.mass = totalMass;
            return clusterOptions;
          },
          clusterNodeProperties: {
            id: `cluster_level_${level}`,
            label: `${childNodes => childNodes.length} nodes\n(${level} hops)`,
            shape: 'database',
            color: '#555555',
            font: { color: '#ffffff', size: 12 },
          },
        };
        
        network.cluster({
          joinCondition: (nodeOptions) => {
            return nodeOptions.level >= level;
          },
          ...clusterOptionsByLevel,
        });
      };
      
      // Cluster level 4+ nodes if graph is very large
      if (nodeCount > 200) {
        clusterByLevel(4);
      } else if (nodeCount > 100) {
        clusterByLevel(5);
      }
    }

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
  }, [data, ownNodeIp]);

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
