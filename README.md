# Dynamic Container Routing Server

A Flask-based routing server that dynamically manages Docker containers for load balancing and auto-scaling of heavy computational tasks.

## Features

- **Dynamic Container Management**: Automatically spawns new containers when needed
- **Load Balancing**: Routes requests to containers with the lowest load
- **Auto-scaling**: Creates new containers when existing ones are busy
- **Auto-cleanup**: Removes idle containers when load is low
- **Real-time Monitoring**: Continuous monitoring of container health and load
- **Graph Visualization**: Provides data for frontend graph visualization

## Architecture

- **Routing Server**: Flask server that manages container lifecycle and routes requests
- **Main Server**: Containerized Flask app with `/heavy` endpoint for computational tasks
- **Container Manager**: Background service that monitors and manages containers

## API Endpoints

### Routing Server (Port 8000)

- `POST /work` - Submit work request (will spawn containers as needed)
- `GET /graph` - Get container graph data for visualization
- `GET /status` - Get current status of all containers
- `GET /health` - Health check endpoint

### Main Server (Dynamic Ports)

- `POST /heavy` - Execute heavy computational work
- `POST /light` - Execute light computational work

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- Docker daemon running

### Quick Start

1. **Build the Docker images**:
   ```bash
   # On Windows
   build.bat
   
   # On Linux/Mac
   chmod +x build.sh
   ./build.sh
   ```

2. **Start the routing server**:
   ```bash
   docker-compose up -d
   ```

3. **Test the setup**:
   ```bash
   # Submit a work request
   curl -X POST http://localhost:8000/work \
        -H "Content-Type: application/json" \
        -d '{"intensity": 3}'
   
   # Check container status
   curl http://localhost:8000/status
   
   # Get graph data
   curl http://localhost:8000/graph
   ```

### Manual Setup

If you prefer to build and run manually:

1. **Build main-server image**:
   ```bash
   cd main-server
   docker build -t main-server:latest .
   cd ..
   ```

2. **Build routing-server image**:
   ```bash
   cd routing-server
   docker build -t routing-server:latest .
   cd ..
   ```

3. **Run the routing server**:
   ```bash
   docker run -d \
     -p 8000:8000 \
     -v /var/run/docker.sock:/var/run/docker.sock \
     --name routing-server \
     routing-server:latest
   ```

## How It Works

### Request Flow

1. Client sends POST request to `/work` endpoint
2. Routing server checks for available containers with low load
3. If no available containers, spawns a new main-server container
4. Routes the request to the selected container's `/heavy` endpoint
5. Returns the response to the client
6. Decrements the container's load counter

### Container Management

- **Monitoring**: Background thread checks container health every 5 seconds
- **Load Tracking**: Each container has a load counter that increments/decrements with requests
- **Auto-scaling**: Creates new containers when existing ones are busy (load > 3)
- **Auto-cleanup**: Removes containers when total load is low (< 2) and multiple containers exist

### Graph Data Format

The `/graph` endpoint returns data compatible with your frontend visualization:

```json
{
  "nodes": [
    {
      "id": "container_id",
      "label": "Container name",
      "color": "green|yellow|red",
      "load": 2,
      "port": 5001
    }
  ],
  "edges": [
    {
      "source": "container_id_1",
      "target": "container_id_2"
    }
  ],
  "timestamp": "2024-01-01T12:00:00",
  "total_containers": 2,
  "total_load": 3
}
```

## Configuration

### Load Thresholds

- **Available Container**: Load < 3
- **Scale Down**: Total load < 2 with multiple containers
- **Container Ready Wait**: 2 seconds after creation

### Port Management

- Routing server runs on port 8000
- Main-server containers run on dynamic ports starting from 5001
- Automatic port conflict resolution

## Monitoring and Logs

- Container creation/removal events are logged
- Load changes are tracked and logged
- Error handling with detailed error messages
- Health check endpoint for monitoring tools

## Testing

### Load Testing

```bash
# Send multiple concurrent requests
for i in {1..10}; do
  curl -X POST http://localhost:8000/work \
       -H "Content-Type: application/json" \
       -d '{"intensity": 2}' &
done
wait
```

### Container Scaling Test

1. Send multiple high-intensity requests
2. Check `/status` to see new containers being created
3. Wait for load to decrease
4. Check `/status` to see containers being removed

## Troubleshooting

### Common Issues

1. **Docker socket permission**: Ensure Docker daemon is accessible
2. **Port conflicts**: Check if ports 8000-5010 are available
3. **Container creation fails**: Check Docker daemon status and available resources

### Logs

```bash
# View routing server logs
docker logs routing-server

# View specific container logs
docker logs <container_id>
```

## Frontend Integration

Use the provided `transformApiResponse` function to process graph data:

```javascript
const response = await fetch('http://localhost:8000/graph');
const apiData = await response.json();
const elements = transformApiResponse(apiData);
```

The graph data includes:
- **Nodes**: Container information with load-based coloring
- **Edges**: Connections between containers
- **Metadata**: Timestamp and aggregate statistics
