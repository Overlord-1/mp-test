import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';

const ROUTING_SERVER = 'http://localhost:8000';

const styles = {
  container: {
    padding: '20px',
    background: '#0a0a1a', // Deeper blue-black background
    minHeight: '100vh',
    fontFamily: "'Courier Prime', monospace",
    color: '#00eaff', // Futuristic light blue text
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
    overflow: 'hidden',
  },
  title: {
    textAlign: 'center',
    fontSize: '2.5rem',
    textShadow: '0 0 15px #00eaff',
    marginBottom: '20px',
  },
  graphContainer: {
    width: '900px', // Larger graph area
    height: '700px',
    position: 'relative',
    background: 'radial-gradient(circle, rgba(12,24,36,0.6) 0%, rgba(10,10,20,0.8) 100%)',
    borderRadius: '16px',
    boxShadow: '0 0 30px rgba(0, 234, 255, 0.2), inset 0 0 15px rgba(0, 234, 255, 0.1)',
    transition: 'all 0.5s ease-in-out',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  },
  svg: {
    width: '100%',
    height: '100%',
  },
  nodeLabel: {
    fontSize: '14px',
    fontWeight: 'bold',
    fill: 'white',
    textShadow: '0 0 5px black',
  },
  infoPanel: {
    position: 'absolute',
    bottom: '20px',
    right: '20px',
    background: 'rgba(2, 2, 8, 0.8)',
    border: '1px solid #00eaff',
    borderRadius: '8px',
    padding: '10px',
    fontSize: '0.9rem',
    boxShadow: '0 0 10px rgba(0, 234, 255, 0.3)',
    zIndex: 10,
  },
  legend: {
    position: 'absolute',
    bottom: '20px',
    left: '20px',
    background: 'rgba(2, 2, 8, 0.8)',
    border: '1px solid #00eaff',
    borderRadius: '8px',
    padding: '10px',
    fontSize: '0.9rem',
    boxShadow: '0 0 10px rgba(0, 234, 255, 0.3)',
    zIndex: 10,
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    marginBottom: '5px',
  },
  legendColor: {
    width: '12px',
    height: '12px',
    borderRadius: '50%',
    marginRight: '8px',
  }
};

// Global CSS for animations
const globalStyles = `
@keyframes pulse {
    0% {
        transform: scale(1);
        box-shadow: 0 0 5px rgba(255, 255, 255, 0.5);
    }
    50% {
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.8);
    }
    100% {
        transform: scale(1);
        box-shadow: 0 0 5px rgba(255, 255, 255, 0.5);
    }
}

@keyframes flow {
    from {
        stroke-dashoffset: 20;
    }
    to {
        stroke-dashoffset: 0;
    }
}


.edge {
    stroke-dasharray: 5 5;
    animation: flow 1s linear infinite;
    stroke-linecap: round;
}

.tooltip {
  position: absolute;
  background: rgba(0,0,0,0.8);
  padding: 8px 12px;
  border-radius: 4px;
  color: white;
  font-size: 12px;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s ease, transform 0.3s ease;
  z-index: 100;
  transform: translate(-50%, -100%);
  white-space: nowrap;
}
.node:hover + .tooltip {
  opacity: 1;
  transform: translate(-50%, -150%);
}
`;

function App() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [stats, setStats] = useState({ total_containers: 0, total_load: 0 });
  const svgRef = useRef(null);

  const fetchGraphData = useCallback(async () => {
    try {
      const response = await axios.get(`${ROUTING_SERVER}/graph`);
      const { nodes: backendNodes, edges: backendEdges, total_containers, total_load } = response.data;
      setNodes(backendNodes);
      setEdges(backendEdges);
      setStats({ total_containers, total_load });
    } catch (error) {
      console.error('Error fetching graph data:', error);
    }
  }, []);

  const renderNetwork = useCallback(() => {
    const svg = svgRef.current;
    if (!svg || !nodes.length) return;

    const width = svg.clientWidth;
    const height = svg.clientHeight;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(centerX, centerY) - 100;
    const nodeMap = new Map(nodes.map(node => [node.id, node]));

    // Use a <g> to group all elements for easier clearing and transformations
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
    svg.innerHTML = '';
    svg.appendChild(g);

    // Calculate node positions once
    const nodePositions = nodes.map((node, index) => {
      const angle = (index * 2 * Math.PI) / nodes.length;
      return {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
        id: node.id
      };
    });
    const positionMap = new Map(nodePositions.map(pos => [pos.id, pos]));

    // Draw edges first (so they are behind nodes)
    edges.forEach(edge => {
      const sourcePos = positionMap.get(edge.source);
      const targetPos = positionMap.get(edge.target);

      if (sourcePos && targetPos) {
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute('x1', sourcePos.x);
        line.setAttribute('y1', sourcePos.y);
        line.setAttribute('x2', targetPos.x);
        line.setAttribute('y2', targetPos.y);
        line.setAttribute('stroke', 'rgba(0, 234, 255, 0.4)');
        line.setAttribute('stroke-width', '2');
        line.classList.add('edge');
        g.appendChild(line);
      }
    });

    // Draw nodes and tooltips
    nodes.forEach((node, index) => {
      const pos = positionMap.get(node.id);
      if (!pos) return;

      const nodeGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
      nodeGroup.classList.add('node');

      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute('cx', pos.x);
      circle.setAttribute('cy', pos.y);
      circle.setAttribute('r', 30);
      circle.setAttribute('fill', node.color || '#4caf50');
      circle.setAttribute('stroke', 'white');
      circle.setAttribute('stroke-width', '2');
      circle.setAttribute('box-shadow', '0 0 10px white');
      nodeGroup.appendChild(circle);

      const shortId = node.label.split('-').pop();
      const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
      text.setAttribute('x', pos.x);
      text.setAttribute('y', pos.y + 5); // Adjust for vertical centering
      text.setAttribute('text-anchor', 'middle');
      text.textContent = shortId;
      text.style.fill = 'white';
      text.style.fontSize = '12px';
      text.style.fontWeight = 'bold';
      nodeGroup.appendChild(text);

      g.appendChild(nodeGroup);
    });
  }, [nodes, edges]);

  useEffect(() => {
    // Add global styles to the document head
    const styleSheet = document.createElement("style");
    styleSheet.type = "text/css";
    styleSheet.innerText = globalStyles;
    document.head.appendChild(styleSheet);
    return () => {
      document.head.removeChild(styleSheet);
    };
  }, []);

  useEffect(() => {
    fetchGraphData();
    const interval = setInterval(fetchGraphData, 1000); // 1-second refresh
    return () => clearInterval(interval);
  }, [fetchGraphData]);

  useEffect(() => {
    renderNetwork();
  }, [nodes, edges, renderNetwork]);

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Container Network Monitoring</h1>
      <div style={styles.graphContainer}>
        <svg ref={svgRef} style={styles.svg}></svg>
      </div>

      <div style={styles.infoPanel}>
        <p>Total Containers: <span style={{ color: '#fff', textShadow: '0 0 5px #fff' }}>{stats.total_containers}</span></p>
        <p>Total Load: <span style={{ color: '#fff', textShadow: '0 0 5px #fff' }}>{stats.total_load}%</span></p>
      </div>

      <div style={styles.legend}>
        <p style={{ fontWeight: 'bold' }}>Load Status</p>
        <div style={styles.legendItem}>
          <div style={{ ...styles.legendColor, background: 'green' }}></div>
          <span>Low (0-25%)</span>
        </div>
        <div style={styles.legendItem}>
          <div style={{ ...styles.legendColor, background: 'yellow' }}></div>
          <span>Medium (26-75%)</span>
        </div>
        <div style={styles.legendItem}>
          <div style={{ ...styles.legendColor, background: 'red' }}></div>
          <span>High (76-100%)</span>
        </div>
      </div>
    </div>
  );
}

export default App;