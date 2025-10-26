import React, { useState, useEffect } from 'react';
import './App.css';
import NetworkGraph from './components/NetworkGraph';
import BandwidthLegend from './components/BandwidthLegend';
import { parseGEXF } from './utils/gexfLoader';

function App() {
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [ownNodeIp, setOwnNodeIp] = useState(null);
  const [stats, setStats] = useState({
    nodes: 0,
    edges: 0,
    participants: 0
  });
  const [lastUpdate, setLastUpdate] = useState(null);
  const [targetInput, setTargetInput] = useState('');
  const [tracing, setTracing] = useState(false);

  useEffect(() => {
    loadNodeInfo();
    loadTopologyData();
    
    // Refresh data every 30 seconds
    const interval = setInterval(loadTopologyData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadNodeInfo = async () => {
    try {
      // Get own node's IP for highlighting
      const response = await fetch('http://localhost:5000/api/node/info');
      if (response.ok) {
        const info = await response.json();
        setOwnNodeIp(info.external_ip);
        console.log('Own node IP:', info.external_ip);
      }
    } catch (err) {
      console.warn('Could not fetch own node info:', err);
    }
  };

  const loadTopologyData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Try to load from API server
      const response = await fetch('http://localhost:5000/api/topology/latest');
      
      if (!response.ok) {
        // If no data yet, show message
        if (response.status === 404) {
          setError('No topology data available yet. Waiting for traceroutes to complete...');
          setLoading(false);
          return;
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const gexfText = await response.text();
      const data = parseGEXF(gexfText);
      
      console.log('Loaded topology data:', data);
      setGraphData(data);
      setStats({
        nodes: data.nodes.length,
        edges: data.edges.length,
        participants: data.nodes.filter(n => n.label && n.label.includes('node-')).length || 1
      });
      setLastUpdate(new Date());
      setLoading(false);
      
    } catch (err) {
      console.error('Failed to load topology:', err);
      setError(`Failed to load topology: ${err.message}`);
      setLoading(false);
    }
  };

  const createSampleData = () => {
    // Sample network topology with bandwidth data for demonstration
    return {
      nodes: [
        { id: '192.168.1.1', label: 'router.local', type: 'participant', color: '#00ff88' },
        { id: '10.0.0.1', label: 'gateway.isp', type: 'hop', color: '#4488ff' },
        { id: '172.16.0.1', label: 'core.router', type: 'hop', color: '#4488ff' },
        { id: '8.8.8.8', label: 'dns.google', type: 'participant', color: '#00ff88' },
        { id: '1.1.1.1', label: 'cloudflare', type: 'participant', color: '#00ff88' },
      ],
      edges: [
        { from: '192.168.1.1', to: '10.0.0.1', bandwidth_mbps: 950, rtt_ms: 2.1 },
        { from: '10.0.0.1', to: '172.16.0.1', bandwidth_mbps: 5500, rtt_ms: 12.5 },
        { from: '172.16.0.1', to: '8.8.8.8', bandwidth_mbps: 150, rtt_ms: 8.3 },
        { from: '172.16.0.1', to: '1.1.1.1', bandwidth_mbps: 75, rtt_ms: 15.7 },
      ]
    };
  };


  const handleReload = () => {
    loadTopologyData();
  };

  const handleExport = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/topology/latest');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `intermap_topology_${new Date().getTime()}.gexf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert('Failed to export topology');
    }
  };

  const handleTraceroute = async () => {
    const target = targetInput.trim();
    if (!target) {
      alert('Please enter an IP address or subnet');
      return;
    }

    setTracing(true);
    try {
      const response = await fetch('http://localhost:5000/api/trace', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ target }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Traceroute failed');
      }

      const result = await response.json();
      alert(`Traceroute started for ${target}\nHops: ${result.hops || 'in progress'}`);
      
      // Reload topology after a short delay to show new data
      setTimeout(loadTopologyData, 2000);
      
    } catch (err) {
      alert(`Traceroute failed: ${err.message}`);
    } finally {
      setTracing(false);
    }
  };

  if (loading && !graphData) {
    return (
      <div className="App">
        <header className="header">
          <h1>🗺️ Intermap - Internet Topology Viewer</h1>
        </header>
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading topology data...</p>
          <p className="hint">Waiting for nodes to discover peers and perform traceroutes</p>
        </div>
      </div>
    );
  }

  if (error && !graphData) {
    return (
      <div className="App">
        <header className="header">
          <h1>🗺️ Intermap - Internet Topology Viewer</h1>
        </header>
        <div className="error">
          <h2>⚠️ {error}</h2>
          <button onClick={handleReload} className="reload-btn">Retry</button>
          <p className="hint">Make sure the Intermap node is running and has discovered peers.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="header">
        <h1>🗺️ Intermap - Internet Topology Viewer</h1>
        
        <div className="traceroute-input">
          <input
            type="text"
            placeholder="IP address or subnet (e.g., 8.8.8.8 or 192.168.1.0/24)"
            value={targetInput}
            onChange={(e) => setTargetInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleTraceroute()}
            disabled={tracing}
          />
          <button onClick={handleTraceroute} disabled={tracing}>
            {tracing ? 'Tracing...' : 'Trace'}
          </button>
        </div>

        <div className="stats">
          <div className="stat-item">
            <div className="stat-value">{stats.nodes}</div>
            <div className="stat-label">Nodes</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{stats.edges}</div>
            <div className="stat-label">Connections</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{stats.participants}</div>
            <div className="stat-label">Participants</div>
          </div>
          {lastUpdate && (
            <div className="stat-item">
              <div className="stat-value">{lastUpdate.toLocaleTimeString()}</div>
              <div className="stat-label">Last Update</div>
            </div>
          )}
        </div>
      </header>
      <div className="graph-container">
        <NetworkGraph data={graphData} ownNodeIp={ownNodeIp} />
        <BandwidthLegend />
        
        {ownNodeIp && (
          <div className="own-node-info">
            ⭐ Your node: <strong>{ownNodeIp}</strong> (highlighted in magenta)
          </div>
        )}
        
        <div className="controls">
          <h3>Controls</h3>
          <button onClick={handleReload}>Reload Data</button>
          <button onClick={handleExport}>Export GEXF</button>
        </div>
      </div>
    </div>
  );
}

export default App;
