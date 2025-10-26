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
    
    // Extract nodes
    const nodesXML = xmlDoc.querySelectorAll('node');
    const nodes = Array.from(nodesXML).map(node => ({
      id: node.getAttribute('id'),
      label: node.getAttribute('label') || node.getAttribute('id'),
    }));
    
    // Extract edges
    const edgesXML = xmlDoc.querySelectorAll('edge');
    const edges = Array.from(edgesXML).map(edge => ({
      from: edge.getAttribute('source'),
      to: edge.getAttribute('target'),
      weight: parseFloat(edge.getAttribute('weight')) || 1,
    }));
    
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
