#!/usr/bin/env python3
"""
Auto-scaling verification test script
"""

import requests
import threading
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def send_work_request(intensity, duration, request_id):
    """Send a work request that will keep a container busy"""
    try:
        start_time = time.time()
        print(f"🚀 Request {request_id}: Starting work with intensity {intensity}")
        
        # Send the request
        response = requests.post(
            f"{BASE_URL}/work",
            json={"intensity": intensity},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            end_time = time.time()
            print(f"✅ Request {request_id}: Completed in {end_time - start_time:.2f}s")
            print(f"   Container: {result.get('container_id', 'N/A')[:12]}...")
            print(f"   Message: {result.get('message', 'N/A')}")
            return result.get('container_id')
        else:
            print(f"❌ Request {request_id}: Failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request {request_id}: Exception - {e}")
        return None

def get_status():
    """Get current system status"""
    try:
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error getting status: {e}")
        return None

def print_status(status_data):
    """Print formatted status information"""
    if not status_data:
        print("❌ Could not get status")
        return
    
    print(f"\n📊 Current Status:")
    print(f"   Total Containers: {status_data['total_containers']}")
    print(f"   Total Load: {status_data['total_load']}")
    print(f"   Timestamp: {status_data['timestamp']}")
    
    if status_data['containers']:
        print(f"   Active Containers:")
        for container_id, info in status_data['containers'].items():
            print(f"     - {info['name']}: Load {info['load']}, Port {info['port']}")
    else:
        print("   No active containers")

def test_autoscaling():
    """Test auto-scaling functionality"""
    print("🧪 AUTO-SCALING VERIFICATION TEST")
    print("=" * 50)
    
    # Step 1: Check initial status
    print("\n1️⃣ Initial Status Check")
    initial_status = get_status()
    print_status(initial_status)
    
    # Step 2: Send multiple concurrent high-intensity requests to trigger scaling
    print("\n2️⃣ Triggering Auto-scaling with Concurrent High-Intensity Requests")
    print("   Sending 5 concurrent requests with intensity 5...")
    
    threads = []
    results = []
    
    # Start multiple threads to send concurrent requests
    for i in range(5):
        thread = threading.Thread(
            target=lambda i=i: results.append(send_work_request(5, 10, i+1))
        )
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Step 3: Check status after scaling
    print("\n3️⃣ Status After Auto-scaling")
    time.sleep(2)  # Give system time to scale
    scaled_status = get_status()
    print_status(scaled_status)
    
    # Step 4: Wait for load to decrease and check auto-cleanup
    print("\n4️⃣ Waiting for Auto-cleanup (30 seconds)...")
    print("   This simulates low load period...")
    
    for i in range(6):
        time.sleep(5)
        status = get_status()
        print(f"   After {i*5 + 5}s: {status['total_containers']} containers, {status['total_load']} total load")
    
    # Step 5: Final status check
    print("\n5️⃣ Final Status Check")
    final_status = get_status()
    print_status(final_status)
    
    # Step 6: Analysis
    print("\n6️⃣ Auto-scaling Analysis")
    print("=" * 30)
    
    initial_containers = initial_status['total_containers'] if initial_status else 0
    scaled_containers = scaled_status['total_containers'] if scaled_status else 0
    final_containers = final_status['total_containers'] if final_status else 0
    
    print(f"Initial containers: {initial_containers}")
    print(f"Peak containers: {scaled_containers}")
    print(f"Final containers: {final_containers}")
    
    # Verify auto-scaling worked
    if scaled_containers > initial_containers:
        print("✅ Auto-scaling UP: Working correctly")
    else:
        print("❌ Auto-scaling UP: Did not trigger")
    
    # Verify auto-cleanup worked
    if final_containers <= initial_containers and final_containers <= scaled_containers:
        print("✅ Auto-cleanup: Working correctly")
    else:
        print("⚠️  Auto-cleanup: May not have triggered (this is normal if load is still high)")
    
    # Check for load balancing
    if scaled_status and scaled_status['containers']:
        loads = [info['load'] for info in scaled_status['containers'].values()]
        if len(set(loads)) > 1:
            print("✅ Load balancing: Working (different containers have different loads)")
        else:
            print("ℹ️  Load balancing: All containers have similar loads")

def test_graph_endpoint():
    """Test the graph endpoint for visualization data"""
    print("\n🎨 Testing Graph Endpoint")
    print("=" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/graph")
        if response.status_code == 200:
            graph_data = response.json()
            print(f"✅ Graph endpoint working")
            print(f"   Nodes: {len(graph_data['nodes'])}")
            print(f"   Edges: {len(graph_data['edges'])}")
            print(f"   Total containers: {graph_data['total_containers']}")
            print(f"   Total load: {graph_data['total_load']}")
            
            # Show node details
            for node in graph_data['nodes']:
                print(f"   Node: {node['label']} - Color: {node['color']}, Load: {node['load']}")
        else:
            print(f"❌ Graph endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Graph endpoint error: {e}")

def main():
    """Run all auto-scaling tests"""
    try:
        # Test if routing server is running
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Routing server is not running or not accessible")
            print("Please start the system with: docker-compose up -d")
            return
    except Exception as e:
        print("❌ Cannot connect to routing server")
        print("Please start the system with: docker-compose up -d")
        return
    
    # Run auto-scaling test
    test_autoscaling()
    
    # Test graph endpoint
    test_graph_endpoint()
    
    print("\n🎉 Auto-scaling verification complete!")
    print("\nNext steps:")
    print("1. Check the routing server logs: docker-compose logs routing-server")
    print("2. Monitor container status: curl http://localhost:8000/status")
    print("3. Get graph data: curl http://localhost:8000/graph")

if __name__ == "__main__":
    main()
