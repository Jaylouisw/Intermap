import React, { useState } from 'react';
import './BandwidthLegend.css';

const BandwidthLegend = () => {
  const [isMinimized, setIsMinimized] = useState(false);

  const categories = [
    { name: 'Gigabit', speed: '≥ 1 Gbps', color: '#00ff00' },
    { name: 'Fast', speed: '≥ 100 Mbps', color: '#88ff00' },
    { name: 'Medium', speed: '≥ 10 Mbps', color: '#ffaa00' },
    { name: 'Slow', speed: '≥ 1 Mbps', color: '#ff4400' },
    { name: 'Very Slow', speed: '< 1 Mbps', color: '#ff0000' },
    { name: 'Unknown', speed: 'No data', color: '#888888' },
  ];

  return (
    <div className={`bandwidth-legend ${isMinimized ? 'minimized' : ''}`}>
      <div className="legend-header">
        <h3>Bandwidth Legend</h3>
        <button 
          className="minimize-btn" 
          onClick={() => setIsMinimized(!isMinimized)}
          aria-label={isMinimized ? "Expand legend" : "Minimize legend"}
        >
          {isMinimized ? '▲' : '▼'}
        </button>
      </div>
      {!isMinimized && (
        <>
          <div className="legend-items">
            {categories.map((cat, index) => (
              <div key={index} className="legend-item">
                <div 
                  className="legend-color" 
                  style={{ backgroundColor: cat.color }}
                />
                <div className="legend-label">
                  <strong>{cat.name}</strong>
                  <span>{cat.speed}</span>
                </div>
              </div>
            ))}
          </div>
          <div className="legend-note">
            Edge colors represent measured bandwidth between nodes.
            Width indicates connection speed (thicker = faster).
          </div>
        </>
      )}
    </div>
  );
};

export default BandwidthLegend;
