/**
 * Intermap - Distributed P2P Internet Topology Mapper
 * Copyright (c) 2025 Jay Wenden
 * Licensed under CC-BY-NC-SA 4.0
 * 
 * GEXF file loader utility
 * Loads and parses GEXF graph files for visualization
 */

export const loadGEXFData = async (filePath) => {
  // TODO: Implement GEXF parsing
  // This will parse GEXF XML format and convert to vis.js format
  
  try {
    const response = await fetch(filePath);
    const xmlText = await response.text();
    
    return parseGEXF(xmlText);
  } catch (error) {
    console.error('Error loading GEXF:', error);
    throw error;
  }
};

export const parseGEXF = (xmlText) => {
  try {
    // Parse XML
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(xmlText, 'text/xml');
    
    // Check for parsing errors
    const parseError = xmlDoc.querySelector('parsererror');
    if (parseError) {
      throw new Error('XML parsing error: ' + parseError.textContent);
    }
    
    // Build attribute definition maps for nodes and edges (id -> title)
    const nodeAttrDefs = {};
    const edgeAttrDefs = {};
    const nodeAttrElems = xmlDoc.querySelectorAll('attributes[class="node"] attribute');
    nodeAttrElems.forEach(attr => {
      const id = attr.getAttribute('id');
      const title = attr.getAttribute('title') || attr.getAttribute('id');
      nodeAttrDefs[id] = title;
    });
    const edgeAttrElems = xmlDoc.querySelectorAll('attributes[class="edge"] attribute');
    edgeAttrElems.forEach(attr => {
      const id = attr.getAttribute('id');
      const title = attr.getAttribute('title') || attr.getAttribute('id');
      edgeAttrDefs[id] = title;
    });

    // Helper to parse attvalue list into a map keyed by attribute title
    const parseAttvalues = (parentNode, defs) => {
      const map = {};
      const attvalues = parentNode.querySelectorAll('attvalue');
      attvalues.forEach(av => {
        const forId = av.getAttribute('for');
        const value = av.getAttribute('value');
        const key = defs[forId] || forId;
        // try to interpret numbers
        const num = Number(value);
        map[key] = Number.isNaN(num) ? value : num;
      });
      return map;
    };

    // Extract nodes (with attributes)
    const nodesXML = xmlDoc.querySelectorAll('node');
    const nodes = Array.from(nodesXML).map(node => {
      const id = node.getAttribute('id');
      const label = node.getAttribute('label') || id;
      const attributes = parseAttvalues(node, nodeAttrDefs);
      return { id, label, attributes };
    });

    // Extract edges (with attributes)
    const edgesXML = xmlDoc.querySelectorAll('edge');
    const edges = Array.from(edgesXML).map(edge => {
      const from = edge.getAttribute('source');
      const to = edge.getAttribute('target');
      const weight = parseFloat(edge.getAttribute('weight')) || 1;
      const attributes = parseAttvalues(edge, edgeAttrDefs);

      // Map common fields to flat names expected by the frontend
      const rtt_ms = attributes.rtt_ms || attributes.rtt || null;
      const bandwidth_download_mbps = attributes.bandwidth_download_mbps || attributes.bandwidth_mbps || attributes.bandwidth || null;
      const bandwidth_upload_mbps = attributes.bandwidth_upload_mbps || null;

      return { from, to, weight, attributes, rtt_ms, bandwidth_download_mbps, bandwidth_upload_mbps };
    });
    
    console.log(`Parsed GEXF: ${nodes.length} nodes, ${edges.length} edges`);
    return { nodes, edges };
  } catch (error) {
    console.error('Error parsing GEXF:', error);
    throw error;
  }
};

export const loadFromIPFS = async (cid) => {
  // TODO: Implement IPFS loading
  // This will fetch GEXF file from IPFS using the CID
  
  const ipfsGateway = 'https://ipfs.io/ipfs/';
  const url = `${ipfsGateway}${cid}`;
  
  return loadGEXFData(url);
};
