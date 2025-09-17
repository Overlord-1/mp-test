import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';

const ROUTING_SERVER = 'http://localhost:8000';

const styles = {
  container: {
    padding: '20px',
    background: '#1a1a1a',
    minHeight: '100vh',
    color: 'white',
  },
  graphContainer: {
    width: '800px',
    height: '600px',
    margin: '0 auto',
    background: '#2a2a2a',
    position: 'relative',
    borderRadius: '8px',
  }
};

function App() {
  const [nodes, setNodes] = useState([]);
  const graphRef = useRef(null);

  const renderNetwork = useCallback(() => {
    const container = graphRef.current;
    if (!container || !nodes.length) return;

    // Clear existing nodes
    container.innerHTML = '';

    const centerX = container.clientWidth / 2;
    const centerY = container.clientHeight / 2;
    const radius = Math.min(centerX, centerY) - 100;

    // Draw edges first (if any nodes are connected)
    if (nodes.length > 1) {
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const angle1 = (i * 2 * Math.PI) / nodes.length;
          const angle2 = (j * 2 * Math.PI) / nodes.length;
          const x1 = centerX + radius * Math.cos(angle1);
          const y1 = centerY + radius * Math.sin(angle1);
          const x2 = centerX + radius * Math.cos(angle2);
          const y2 = centerY + radius * Math.sin(angle2);

          const edge = document.createElement('div');
          const length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
          const angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;

          edge.style.cssText = `
            position: absolute;
            left: ${x1}px;
            top: ${y1}px;
            width: ${length}px;
            height: 2px;
            background: rgba(255, 255, 255, 0.3);
            transform: rotate(${angle}deg);
            transform-origin: left center;
            z-index: 1;
          `;
          container.appendChild(edge);
        }
      }
    }

    nodes.forEach((node, index) => {
      const angle = (index * 2 * Math.PI) / nodes.length;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      
      const nodeDiv = document.createElement('div');
      nodeDiv.style.cssText = `
        position: absolute;
        left: ${x - 40}px;
        top: ${y - 40}px;
        width: 80px;
        height: 80px;
        background: ${node.color || '#4caf50'};
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        border: 3px solid white;
        transition: all 0.3s ease;
        z-index: 2;
      `;
      
      const shortId = node.label.split('-').pop();
      nodeDiv.innerHTML = `
        ${shortId}
        <div style="
          position: absolute;
          top: -25px;
          left: 50%;
          transform: translateX(-50%);
          background: rgba(0,0,0,0.8);
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          opacity: 0;
          transition: opacity 0.3s;
          white-space: nowrap;
        ">Port: ${node.port} | Load: ${node.load}%</div>
      `;
      
      // Add hover effect for tooltip
      nodeDiv.addEventListener('mouseenter', () => {
        nodeDiv.querySelector('div').style.opacity = '1';
      });
      nodeDiv.addEventListener('mouseleave', () => {
        nodeDiv.querySelector('div').style.opacity = '0';
      });
      container.appendChild(nodeDiv);
    });
  }, [nodes]);

  const fetchGraphData = useCallback(async () => {
    try {
      const response = await axios.get(`${ROUTING_SERVER}/graph`);
      const { nodes: backendNodes } = response.data;
      console.log('Fetched nodes:', backendNodes);
      setNodes(backendNodes);
    } catch (error) {
      console.error('Error fetching graph data:', error);
    }
  }, []);

  useEffect(() => {
    fetchGraphData();
    const interval = setInterval(fetchGraphData, 1000); // Increased refresh rate to 1 second
    return () => clearInterval(interval);
  }, [fetchGraphData]);

  useEffect(() => {
    renderNetwork();
  }, [nodes, renderNetwork]);

  return (
    <div style={styles.container}>
      <h1 style={{textAlign: 'center'}}>Container Network</h1>
      <div ref={graphRef} style={styles.graphContainer} />
    </div>
  );
}

export default App;