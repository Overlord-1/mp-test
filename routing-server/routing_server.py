from flask import Flask, request, jsonify
from flask_cors import CORS
import docker
import threading
import time
import requests
import json
from datetime import datetime
import logging
from typing import Dict, List, Optional
import uuid

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContainerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.containers: Dict[str, dict] = {}
        self.container_loads: Dict[str, int] = {}
        self.monitoring_thread = None
        self.monitoring_active = True
        self.container_logs: Dict[str, List[dict]] = {}
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start the background monitoring thread"""
        if self.monitoring_thread is None or not self.monitoring_thread.is_alive():
            self.monitoring_thread = threading.Thread(target=self._monitor_containers, daemon=True)
            self.monitoring_thread.start()
            logger.info("Container monitoring started")
    
    def _monitor_containers(self):
        """Continuously monitor containers and manage their lifecycle"""
        while self.monitoring_active:
            try:
                # Check each container's status
                containers_to_remove = []
                for container_id, container_info in list(self.containers.items()):
                    try:
                        container = self.client.containers.get(container_id)
                        
                        # Check if container is running
                        if container.status != 'running':
                            logger.info(f"Container {container_id} is not running, removing from tracking")
                            containers_to_remove.append(container_id)
                            continue
                        
                        # Check container load (simplified - you can implement more sophisticated load checking)
                        load = self._get_container_load(container_id)
                        self.container_loads[container_id] = load
                        
                        # Log container activity
                        self._log_container_activity(container_id, container_info, load)
                        
                    except docker.errors.NotFound:
                        logger.info(f"Container {container_id} not found, removing from tracking")
                        containers_to_remove.append(container_id)
                    except Exception as e:
                        logger.error(f"Error monitoring container {container_id}: {e}")
                
                # Remove dead containers
                for container_id in containers_to_remove:
                    self._remove_container(container_id)
                
                # Scale down if load is low
                self._scale_down_if_needed()
                
                time.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)
    
    def _get_container_load(self, container_id: str) -> int:
        """Get the current load of a container"""
        # Simplified load calculation - you can implement more sophisticated metrics
        return self.container_loads.get(container_id, 0)
    
    def _log_container_activity(self, container_id: str, container_info: dict, load: int):
        """Log container activity for the graph endpoint"""
        if container_id not in self.container_logs:
            self.container_logs[container_id] = []
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'container_id': container_id,
            'load': load,
            'status': 'running',
            'port': container_info.get('port', 5000)
        }
        
        self.container_logs[container_id].append(log_entry)
        
        # Keep only last 100 entries per container
        if len(self.container_logs[container_id]) > 100:
            self.container_logs[container_id] = self.container_logs[container_id][-100:]
    
    def _scale_down_if_needed(self):
        """Scale down containers if total load is low"""
        total_load = sum(self.container_loads.values())
        total_containers = len(self.containers)
        
        # If we have more than 1 container and total load is very low, scale down
        if total_containers > 1 and total_load < 2:
            # Find the container with lowest load
            if self.container_loads:
                lowest_load_container = min(self.container_loads.items(), key=lambda x: x[1])
                container_id = lowest_load_container[0]
                logger.info(f"Scaling down - removing container {container_id} with load {lowest_load_container[1]}")
                self._remove_container(container_id)
    
    def _remove_container(self, container_id: str):
        """Remove a container and clean up tracking"""
        try:
            if container_id in self.containers:
                container_info = self.containers[container_id]
                del self.containers[container_id]
                if container_id in self.container_loads:
                    del self.container_loads[container_id]
                if container_id in self.container_logs:
                    del self.container_logs[container_id]
                
                # Stop and remove the container
                try:
                    container = self.client.containers.get(container_id)
                    container.stop(timeout=5)
                    container.remove()
                    logger.info(f"Removed container {container_id}")
                except docker.errors.NotFound:
                    pass
                    
        except Exception as e:
            logger.error(f"Error removing container {container_id}: {e}")
    
    def get_available_container(self) -> Optional[str]:
        """Get an available container with lowest load"""
        if not self.containers:
            return None
        
        # Find container with lowest load
        available_containers = [(cid, load) for cid, load in self.container_loads.items() 
                               if load < 3]  # Threshold for "available"
        
        if available_containers:
            return min(available_containers, key=lambda x: x[1])[0]
        
        return None
    
    def create_new_container(self) -> str:
        """Create a new main-server container"""
        try:
            # Generate unique container name
            container_name = f"main-server-{uuid.uuid4().hex[:8]}"
            
            # Find available port
            port = self._find_available_port()
            
            # Check if image exists locally
            try:
                self.client.images.get('main-server:latest')
                logger.info("Using existing main-server:latest image")
            except docker.errors.ImageNotFound:
                logger.error("main-server:latest image not found locally")
                logger.error("Please build the main-server image first using:")
                logger.error("cd main-server && docker build -t main-server:latest .")
                raise Exception("main-server:latest image not found. Please build it first.")
            
            # Get the current network name for the routing server
            current_network = None
            try:
                # Get the routing server's network
                routing_container = self.client.containers.get('mp-test-routing-server-1')
                routing_container.reload()
                network_settings = routing_container.attrs.get('NetworkSettings', {})
                networks = network_settings.get('Networks', {})
                current_network = list(networks.keys())[0] if networks else None
                logger.info(f"Using network: {current_network}")
            except Exception as e:
                logger.warning(f"Could not get current network: {e}")
            
            # Run the container on the same network as the routing server
            container = self.client.containers.run(
                image='main-server:latest',
                name=container_name,
                ports={5000: port},
                detach=True,
                environment={'PYTHONUNBUFFERED': '1'},
                network=current_network,  # Use the same network as routing server
                remove=False,  # Don't auto-remove on exit
                auto_remove=False  # Keep container for debugging
            )
            
            container_id = container.id
            
            # Wait for container to be ready and verify it's responding
            max_retries = 15
            container_ready = False
            
            for attempt in range(max_retries):
                time.sleep(2)  # Wait longer between attempts
                try:
                    # Check if container is actually running
                    container.reload()
                    if container.status != 'running':
                        logger.warning(f"Container {container_name} status: {container.status}")
                        continue
                    
                    # Try to connect to the container to verify it's ready
                    container_url = f"http://host.docker.internal:{port}"
                    response = requests.get(f"{container_url}/", timeout=3)
                    if response.status_code in [200, 404]:  # 404 is ok, means Flask is running
                        logger.info(f"Container {container_name} is ready after {attempt + 1} attempts")
                        container_ready = True
                        break
                except requests.exceptions.RequestException as e:
                    logger.debug(f"Attempt {attempt + 1}: Container not ready yet - {e}")
                    if attempt == max_retries - 1:
                        logger.warning(f"Container {container_name} may not be fully ready")
            
            if not container_ready:
                logger.error(f"Container {container_name} failed to become ready")
                # Don't track failed containers
                try:
                    container.stop()
                    container.remove()
                except:
                    pass
                raise Exception(f"Container {container_name} failed to start properly")
            
            # Track the container
            self.containers[container_id] = {
                'name': container_name,
                'port': port,
                'created_at': datetime.now().isoformat()
            }
            self.container_loads[container_id] = 0
            
            logger.info(f"Created new container {container_name} with ID {container_id} on port {port}")
            return container_id
            
        except Exception as e:
            logger.error(f"Error creating new container: {e}")
            raise
    
    def _find_available_port(self) -> int:
        """Find an available port for the new container starting from 5002"""
        used_ports = {info['port'] for info in self.containers.values()}
        port = 5002  # Start from 5002 to avoid using 5001
        while port in used_ports:
            port += 1
        return port
    
    
    def get_container_url(self, container_id: str) -> str:
        """Get the URL for a container"""
        if container_id in self.containers:
            port = self.containers[container_id]['port']
            # Try to get the container's IP address directly
            try:
                container = self.client.containers.get(container_id)
                container.reload()
                
                # Get the container's IP address from network settings
                network_settings = container.attrs.get('NetworkSettings', {})
                networks = network_settings.get('Networks', {})
                
                # Try to find the IP from bridge network or default network
                for network_name, network_info in networks.items():
                    if network_name != 'host':
                        ip_address = network_info.get('IPAddress')
                        if ip_address:
                            logger.info(f"Using container IP {ip_address} for {container_id}")
                            return f"http://{ip_address}:5000"
                
                # Fallback to localhost (this won't work from inside Docker)
                logger.warning(f"Could not get container IP for {container_id}, using localhost fallback")
                return f"http://localhost:{port}"
                
            except Exception as e:
                logger.warning(f"Error getting container IP for {container_id}: {e}")
                return f"http://localhost:{port}"
        return None
    
    def increment_load(self, container_id: str):
        """Increment the load counter for a container"""
        if container_id in self.container_loads:
            self.container_loads[container_id] += 1
    
    def decrement_load(self, container_id: str):
        """Decrement the load counter for a container"""
        if container_id in self.container_loads:
            self.container_loads[container_id] = max(0, self.container_loads[container_id] - 1)
    
    def get_graph_data(self) -> dict:
        """Get data for the graph visualization"""
        nodes = []
        edges = []
        
        for container_id, container_info in self.containers.items():
            load = self.container_loads.get(container_id, 0)
            
            # Determine node color based on load
            if load == 0:
                color = 'green'
            elif load < 3:
                color = 'yellow'
            else:
                color = 'red'
            
            nodes.append({
                'id': container_id,
                'label': f"Container {container_info['name']}",
                'color': color,
                'load': load,
                'port': container_info['port']
            })
        
        # Add edges between containers (simplified - you can implement more sophisticated connections)
        container_ids = list(self.containers.keys())
        for i in range(len(container_ids)):
            for j in range(i + 1, len(container_ids)):
                edges.append({
                    'source': container_ids[i],
                    'target': container_ids[j]
                })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'timestamp': datetime.now().isoformat(),
            'total_containers': len(self.containers),
            'total_load': sum(self.container_loads.values())
        }
    
    def shutdown(self):
        """Shutdown the container manager"""
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        # Clean up all containers
        for container_id in list(self.containers.keys()):
            self._remove_container(container_id)

# Global container manager instance
container_manager = ContainerManager()

@app.route('/work', methods=['POST'])
def work():
    """Handle work requests by routing to available containers"""
    try:
        # Get request data
        data = request.json or {}
        intensity = data.get('intensity', 1)
        
        # Find an available container
        container_id = container_manager.get_available_container()
        
        # If no available container, create a new one
        if container_id is None:
            logger.info("No available containers, creating new one")
            container_id = container_manager.create_new_container()
        
        # Increment load for the container
        container_manager.increment_load(container_id)
        
        try:
            # Get container URL and make request
            container_url = container_manager.get_container_url(container_id)
            if not container_url:
                raise Exception(f"Could not get URL for container {container_id}")
            
            # Make request to the container's /heavy endpoint
            response = requests.post(
                f"{container_url}/heavy",
                json={'intensity': intensity},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                result['container_id'] = container_id
                result['container_url'] = container_url
                return jsonify(result)
            else:
                raise Exception(f"Container returned status {response.status_code}")
                
        finally:
            # Always decrement load when done
            container_manager.decrement_load(container_id)
    
    except Exception as e:
        logger.error(f"Error handling work request: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/graph', methods=['GET'])
def graph():
    """Get container graph data for visualization"""
    try:
        return jsonify(container_manager.get_graph_data())
    except Exception as e:
        logger.error(f"Error getting graph data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Get current status of all containers"""
    try:
        status_data = {
            'containers': {},
            'total_containers': len(container_manager.containers),
            'total_load': sum(container_manager.container_loads.values()),
            'timestamp': datetime.now().isoformat()
        }
        
        for container_id, container_info in container_manager.containers.items():
            load = container_manager.container_loads.get(container_id, 0)
            status_data['containers'][container_id] = {
                'name': container_info['name'],
                'port': container_info['port'],
                'load': load,
                'created_at': container_info['created_at']
            }
        
        return jsonify(status_data)
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=8000, debug=True)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        container_manager.shutdown()
