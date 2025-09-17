# 🎬 Container Auto-scaling System Demo

A comprehensive demonstration of a dynamic container auto-scaling system with real-time monitoring and interactive visualization.

## 🚀 Quick Start

### **Windows:**
```bash
start_demo.bat
```

### **Linux/Mac:**
```bash
chmod +x start_demo.sh
./start_demo.sh
```

## 📋 What You'll See

### **1. Backend System (Port 8000)**
- **Dynamic Container Management**: Automatically creates/destroys containers
- **Auto-scaling**: Scales up during high load, scales down during low load
- **Load Balancing**: Distributes requests across available containers
- **Real-time Monitoring**: Continuous health checks and status updates

### **2. Interactive Web Dashboard (Port 3000)**
- **Live Graph Visualization**: Real-time container network graph
- **Interactive Controls**: Send requests and monitor responses
- **System Statistics**: Live container count, load metrics
- **Activity Logs**: Real-time system activity monitoring

## 🎯 Demo Scenarios

### **Scenario 1: Basic Operation**
- System starts with no containers
- First request creates a new container
- Subsequent requests use existing containers

### **Scenario 2: Auto-scaling Under Load**
- Multiple concurrent requests trigger container creation
- System scales up to handle increased load
- Load balancing distributes work across containers

### **Scenario 3: Load Balancing**
- Rapid requests demonstrate load distribution
- Shows how system manages multiple containers
- Demonstrates efficient resource utilization

### **Scenario 4: Real-time Visualization**
- Graph updates live with container changes
- Color-coded nodes show container status:
  - 🟢 Green: No load (healthy)
  - 🟡 Yellow: Medium load (warning)
  - 🔴 Red: High load (critical)
- Interactive nodes show detailed container info

### **Scenario 5: Auto-cleanup**
- System automatically removes unused containers
- Demonstrates efficient resource management
- Shows scaling down during low load periods

## 🎮 Interactive Features

### **Web Dashboard Controls:**
- **Work Intensity Slider**: Adjust computational load (1-10)
- **Request Count**: Send single or multiple requests
- **Send Request**: Submit individual work requests
- **Send Bulk Requests**: Submit multiple concurrent requests
- **Auto Refresh**: Toggle automatic graph updates
- **Refresh Interval**: Control update frequency (1-10 seconds)

### **Graph Interactions:**
- **Zoom/Pan**: Navigate the container network
- **Node Selection**: Click containers for detailed information
- **Hover Effects**: See container details on hover
- **Fit to Screen**: Auto-arrange graph layout
- **Reset View**: Restore default graph settings

## 📊 System Metrics

### **Real-time Statistics:**
- **Total Containers**: Current number of running containers
- **Total Load**: Aggregate load across all containers
- **Last Update**: Timestamp of last status update
- **Connection Status**: Backend connectivity indicator

### **Container Details:**
- **Container ID**: Unique identifier
- **Load Level**: Current computational load
- **Port**: Network port assignment
- **Creation Time**: When container was created
- **Status**: Running/Stopped/Error

## 🔧 Technical Details

### **Auto-scaling Thresholds:**
- **Scale UP**: When container load > 3
- **Scale DOWN**: When total load < 2 and multiple containers exist
- **Monitoring**: Health checks every 5 seconds
- **Load Tracking**: Increments on request, decrements on completion

### **Network Architecture:**
- **Routing Server**: Manages container lifecycle and request routing
- **Main Servers**: Handle computational workloads
- **Docker Network**: Isolated container communication
- **Load Balancing**: Intelligent request distribution

## 🎨 Frontend Features

### **Modern UI/UX:**
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Live data refresh
- **Interactive Graphs**: Powered by vis.js network visualization
- **Beautiful Animations**: Smooth transitions and effects
- **Dark/Light Theme**: Professional color scheme

### **Visualization Elements:**
- **Network Graph**: Container relationship visualization
- **Color Coding**: Status-based node coloring
- **Dynamic Layout**: Physics-based graph arrangement
- **Interactive Nodes**: Clickable container details
- **Real-time Edges**: Container connection visualization

## 📱 Browser Compatibility

- **Chrome**: ✅ Full support
- **Firefox**: ✅ Full support
- **Safari**: ✅ Full support
- **Edge**: ✅ Full support

## 🛠️ Troubleshooting

### **Common Issues:**

**Port 8000 already in use:**
```bash
docker-compose down
docker system prune -f
docker-compose up -d
```

**Port 3000 already in use:**
```bash
# Find and kill process using port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**Containers not scaling:**
```bash
# Check logs
docker-compose logs routing-server
```

**Frontend not loading:**
```bash
# Check if frontend server is running
cd frontend
python server.py
```

## 🎓 Educational Value

This demo showcases:
- **Microservices Architecture**: Container-based service design
- **Auto-scaling Patterns**: Dynamic resource management
- **Load Balancing**: Request distribution strategies
- **Real-time Monitoring**: System health tracking
- **Interactive Visualization**: Data presentation techniques
- **RESTful APIs**: Service communication patterns

## 🚀 Production Considerations

For production deployment:
- **Security**: Add authentication and HTTPS
- **Monitoring**: Integrate with monitoring tools (Prometheus, Grafana)
- **Logging**: Centralized logging with ELK stack
- **Persistence**: Database for container state
- **Health Checks**: Comprehensive health monitoring
- **Scaling Policies**: Configurable scaling thresholds

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the logs: `docker-compose logs`
3. Verify all services are running: `docker ps`
4. Test API endpoints: `curl http://localhost:8000/health`

---

**🎉 Enjoy exploring the container auto-scaling system!**
