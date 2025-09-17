// Container Auto-scaling Dashboard JavaScript
class ContainerDashboard {
    constructor() {
        this.network = null;
        this.nodes = new vis.DataSet();
        this.edges = new vis.DataSet();
        this.refreshInterval = null;
        this.isConnected = false;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeGraph();
        this.startAutoRefresh();
        this.checkConnection();
        
        this.addLog('System initialized', 'info');
    }

    setupEventListeners() {
        // Control buttons
        document.getElementById('sendRequestBtn').addEventListener('click', () => this.sendRequest());
        document.getElementById('sendBulkBtn').addEventListener('click', () => this.sendBulkRequests());
        document.getElementById('fitGraph').addEventListener('click', () => this.fitGraph());
        document.getElementById('resetGraph').addEventListener('click', () => this.resetGraph());
        document.getElementById('clearLogs').addEventListener('click', () => this.clearLogs());

        // Intensity slider
        const intensityInput = document.getElementById('intensityInput');
        const intensityValue = document.getElementById('intensityValue');
        intensityInput.addEventListener('input', (e) => {
            intensityValue.textContent = e.target.value;
        });

        // Auto refresh toggle
        document.getElementById('autoRefresh').addEventListener('change', (e) => {
            if (e.target.checked) {
                this.startAutoRefresh();
            } else {
                this.stopAutoRefresh();
            }
        });

        // Refresh interval
        document.getElementById('refreshInterval').addEventListener('change', (e) => {
            if (this.refreshInterval) {
                this.stopAutoRefresh();
                this.startAutoRefresh();
            }
        });
    }

    initializeGraph() {
        const container = document.getElementById('networkGraph');
        const data = {
            nodes: this.nodes,
            edges: this.edges
        };

        const options = {
            nodes: {
                shape: 'dot',
                size: 30,
                font: {
                    size: 14,
                    color: '#ffffff'
                },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                width: 2,
                color: { color: '#848484' },
                smooth: {
                    type: 'continuous'
                }
            },
            physics: {
                enabled: true,
                stabilization: { iterations: 100 },
                barnesHut: {
                    gravitationalConstant: -2000,
                    centralGravity: 0.3,
                    springLength: 95,
                    springConstant: 0.04,
                    damping: 0.09,
                    avoidOverlap: 0.1
                }
            },
            interaction: {
                hover: true,
                selectConnectedEdges: false
            }
        };

        this.network = new vis.Network(container, data, options);

        // Handle node selection
        this.network.on('selectNode', (params) => {
            this.showContainerDetails(params.nodes[0]);
        });

        // Handle node hover
        this.network.on('hoverNode', (params) => {
            this.network.setOptions({
                nodes: {
                    font: {
                        size: 16
                    }
                }
            });
        });

        this.network.on('blurNode', (params) => {
            this.network.setOptions({
                nodes: {
                    font: {
                        size: 14
                    }
                }
            });
        });
    }

    async checkConnection() {
        try {
            const response = await axios.get('http://localhost:8000/health', { timeout: 5000 });
            if (response.status === 200) {
                this.setConnectionStatus(true);
                this.updateStatus();
            } else {
                this.setConnectionStatus(false);
            }
        } catch (error) {
            this.setConnectionStatus(false);
        }
    }

    setConnectionStatus(connected) {
        this.isConnected = connected;
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        const connectionStatus = document.getElementById('connectionStatus');

        if (connected) {
            statusDot.className = 'status-dot connected';
            statusText.textContent = 'Connected';
            connectionStatus.textContent = 'Connected';
        } else {
            statusDot.className = 'status-dot';
            statusText.textContent = 'Disconnected';
            connectionStatus.textContent = 'Disconnected';
        }
    }

    async updateStatus() {
        if (!this.isConnected) {
            this.checkConnection();
            return;
        }

        try {
            this.addLog('Fetching status from backend...', 'info');
            const response = await axios.get('http://localhost:8000/status');
            const statusData = response.data;

            this.addLog(`Status received: ${statusData.total_containers} containers, ${statusData.total_load} load`, 'info');

            // Update stats
            document.getElementById('totalContainers').textContent = statusData.total_containers;
            document.getElementById('totalLoad').textContent = statusData.total_load;
            document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();

            // Update graph
            this.updateGraph(statusData);

        } catch (error) {
            this.addLog(`Error updating status: ${error.message}`, 'error');
            this.setConnectionStatus(false);
        }
    }

    async updateGraph(statusData) {
        this.addLog('Updating graph visualization...', 'info');
        const nodes = [];
        const edges = [];

        // Create nodes from containers
        Object.entries(statusData.containers).forEach(([containerId, info]) => {
            this.addLog(`Creating node for container: ${info.name}`, 'info');
            const node = {
                id: containerId,
                label: info.name,
                color: {
                    background: this.getContainerColor(info.load),
                    border: this.getContainerBorderColor(info.load),
                    highlight: {
                        background: this.getContainerColor(info.load, true),
                        border: this.getContainerBorderColor(info.load, true)
                    }
                },
                title: `Container: ${info.name}\nLoad: ${info.load}\nPort: ${info.port}\nCreated: ${info.created_at}`
            };
            nodes.push(node);
        });

        // Create edges between containers (simplified)
        const containerIds = Object.keys(statusData.containers);
        for (let i = 0; i < containerIds.length; i++) {
            for (let j = i + 1; j < containerIds.length; j++) {
                edges.push({
                    from: containerIds[i],
                    to: containerIds[j],
                    color: { color: '#95a5a6' }
                });
            }
        }

        this.addLog(`Graph update: ${nodes.length} nodes, ${edges.length} edges`, 'info');

        // Update the graph
        this.nodes.clear();
        this.edges.clear();
        this.nodes.add(nodes);
        this.edges.add(edges);

        // Force graph redraw
        if (this.network) {
            this.network.redraw();
        }
    }

    getContainerColor(load, highlight = false) {
        if (load === 0) {
            return highlight ? '#2ecc71' : '#27ae60'; // Green
        } else if (load < 3) {
            return highlight ? '#f1c40f' : '#f39c12'; // Yellow
        } else {
            return highlight ? '#e74c3c' : '#c0392b'; // Red
        }
    }

    getContainerBorderColor(load, highlight = false) {
        if (load === 0) {
            return highlight ? '#27ae60' : '#2ecc71';
        } else if (load < 3) {
            return highlight ? '#f39c12' : '#f1c40f';
        } else {
            return highlight ? '#c0392b' : '#e74c3c';
        }
    }

    showContainerDetails(containerId) {
        // This would show detailed information about the selected container
        const containerDetails = document.getElementById('containerDetails');
        containerDetails.innerHTML = `
            <div class="container-detail">
                <h4>Container Details</h4>
                <p><strong>ID:</strong> ${containerId.substring(0, 12)}...</p>
                <p><strong>Status:</strong> Active</p>
                <p><strong>Type:</strong> Main Server</p>
                <p><strong>Network:</strong> Bridge</p>
            </div>
        `;
    }

    async sendRequest() {
        if (!this.isConnected) {
            this.addLog('Cannot send request: Not connected to server', 'error');
            return;
        }

        const intensity = document.getElementById('intensityInput').value;
        const requestId = Date.now();

        this.addLog(`Sending work request (intensity: ${intensity})...`, 'info');

        try {
            const response = await axios.post('http://localhost:8000/work', {
                intensity: parseInt(intensity)
            });

            if (response.status === 200) {
                const result = response.data;
                this.addLog(`Request completed in ${result.time_taken.toFixed(2)}s`, 'success');
                this.addLog(`Container: ${result.container_id.substring(0, 12)}...`, 'info');
                
                // Update the graph immediately
                this.updateStatus();
            }
        } catch (error) {
            this.addLog(`Request failed: ${error.response?.data?.error || error.message}`, 'error');
        }
    }

    async sendBulkRequests() {
        if (!this.isConnected) {
            this.addLog('Cannot send requests: Not connected to server', 'error');
            return;
        }

        const intensity = document.getElementById('intensityInput').value;
        const count = document.getElementById('requestCount').value;
        
        this.addLog(`Sending ${count} bulk requests (intensity: ${intensity})...`, 'info');

        const promises = [];
        for (let i = 0; i < count; i++) {
            promises.push(
                axios.post('http://localhost:8000/work', {
                    intensity: parseInt(intensity)
                })
            );
        }

        try {
            const responses = await Promise.all(promises);
            const successful = responses.filter(r => r.status === 200).length;
            this.addLog(`${successful}/${count} bulk requests completed successfully`, 'success');
            
            // Update the graph
            this.updateStatus();
        } catch (error) {
            this.addLog(`Bulk requests failed: ${error.message}`, 'error');
        }
    }

    fitGraph() {
        if (this.network) {
            this.network.fit();
        }
    }

    resetGraph() {
        if (this.network) {
            this.network.setOptions({
                physics: {
                    enabled: true
                }
            });
            this.network.fit();
        }
    }

    addLog(message, type = 'info') {
        const logContainer = document.getElementById('logContainer');
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${type}`;
        
        const time = new Date().toLocaleTimeString();
        logEntry.innerHTML = `
            <span class="log-time">${time}</span>
            <span class="log-message">${message}</span>
        `;
        
        logContainer.appendChild(logEntry);
        logContainer.scrollTop = logContainer.scrollHeight;

        // Keep only last 50 log entries
        const entries = logContainer.querySelectorAll('.log-entry');
        if (entries.length > 50) {
            entries[0].remove();
        }
    }

    clearLogs() {
        document.getElementById('logContainer').innerHTML = '';
        this.addLog('Logs cleared', 'info');
    }

    startAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }

        const interval = parseInt(document.getElementById('refreshInterval').value) * 1000;
        this.refreshInterval = setInterval(() => {
            this.updateStatus();
        }, interval);

        this.addLog(`Auto-refresh started (${interval/1000}s interval)`, 'info');
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
            this.addLog('Auto-refresh stopped', 'info');
        }
    }
}

// Initialize the dashboard when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new ContainerDashboard();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        window.dashboard.stopAutoRefresh();
    } else {
        if (document.getElementById('autoRefresh').checked) {
            window.dashboard.startAutoRefresh();
        }
    }
});
