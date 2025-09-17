#!/usr/bin/env python3
"""
Live Demo Script for Container Auto-scaling System
"""

import requests
import threading
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🎬 {title}")
    print("=" * 60)

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n{step} {description}")
    print("-" * 40)

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

def print_status(status_data, label=""):
    """Print formatted status information"""
    if not status_data:
        print("❌ Could not get status")
        return
    
    print(f"📊 {label}Status:")
    print(f"   🐳 Total Containers: {status_data['total_containers']}")
    print(f"   ⚖️  Total Load: {status_data['total_load']}")
    
    if status_data['containers']:
        print(f"   📋 Active Containers:")
        for container_id, info in status_data['containers'].items():
            print(f"     • {info['name']}: Load {info['load']}, Port {info['port']}")
    else:
        print("   📋 No active containers")

def send_demo_request(intensity, request_id):
    """Send a demo work request"""
    try:
        print(f"🚀 Sending request {request_id} (intensity: {intensity})...")
        
        response = requests.post(
            f"{BASE_URL}/work",
            json={"intensity": intensity},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Request {request_id} completed in {result.get('time_taken', 0):.2f}s")
            print(f"   Container: {result.get('container_id', 'N/A')[:12]}...")
            return result.get('container_id')
        else:
            print(f"❌ Request {request_id} failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Request {request_id} error: {e}")
        return None

def demo_scenario_1_basic_operation():
    """Demo Scenario 1: Basic Operation"""
    print_step("SCENARIO 1", "Basic System Operation")
    
    # Check initial status
    print("1. Checking initial system status...")
    initial_status = get_status()
    print_status(initial_status, "Initial ")
    
    # Send a simple request
    print("\n2. Sending a work request...")
    container_id = send_demo_request(3, 1)
    
    # Check status after request
    print("\n3. Checking status after request...")
    time.sleep(1)
    after_status = get_status()
    print_status(after_status, "After Request ")

def demo_scenario_2_auto_scaling():
    """Demo Scenario 2: Auto-scaling"""
    print_step("SCENARIO 2", "Auto-scaling Under Load")
    
    # Check initial status
    print("1. Initial system status...")
    initial_status = get_status()
    print_status(initial_status, "Initial ")
    
    # Send multiple concurrent requests
    print("\n2. Sending 4 concurrent high-intensity requests...")
    print("   This should trigger auto-scaling...")
    
    threads = []
    results = []
    
    for i in range(4):
        thread = threading.Thread(
            target=lambda i=i: results.append(send_demo_request(8, i+1))
        )
        threads.append(thread)
        thread.start()
        time.sleep(0.5)  # Small delay between starting threads
    
    # Monitor during scaling
    print("\n3. Monitoring system during scaling...")
    time.sleep(3)
    scaling_status = get_status()
    print_status(scaling_status, "During Scaling ")
    
    # Wait for completion
    print("\n4. Waiting for all requests to complete...")
    for thread in threads:
        thread.join()
    
    # Check final status
    print("\n5. Final status after scaling...")
    time.sleep(2)
    final_status = get_status()
    print_status(final_status, "Final ")

def demo_scenario_3_load_balancing():
    """Demo Scenario 3: Load Balancing"""
    print_step("SCENARIO 3", "Load Balancing")
    
    print("1. Sending rapid requests to demonstrate load balancing...")
    
    # Send requests rapidly
    for i in range(6):
        send_demo_request(2, i+1)
        time.sleep(0.3)
    
    # Check status
    print("\n2. Checking load distribution...")
    time.sleep(1)
    status = get_status()
    print_status(status, "Load Balancing ")

def demo_scenario_4_graph_data():
    """Demo Scenario 4: Graph Data"""
    print_step("SCENARIO 4", "Graph Data for Visualization")
    
    print("1. Fetching graph data...")
    try:
        response = requests.get(f"{BASE_URL}/graph")
        if response.status_code == 200:
            graph_data = response.json()
            print("✅ Graph data retrieved successfully!")
            print(f"   📊 Nodes: {len(graph_data['nodes'])}")
            print(f"   🔗 Edges: {len(graph_data['edges'])}")
            print(f"   🐳 Total containers: {graph_data['total_containers']}")
            print(f"   ⚖️  Total load: {graph_data['total_load']}")
            
            # Show node details
            if graph_data['nodes']:
                print(f"   📋 Node details:")
                for node in graph_data['nodes']:
                    color_emoji = "🟢" if node['color'] == 'green' else "🟡" if node['color'] == 'yellow' else "🔴"
                    print(f"     {color_emoji} {node['label']}: Load {node['load']}")
        else:
            print(f"❌ Failed to get graph data: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting graph data: {e}")

def demo_scenario_5_auto_cleanup():
    """Demo Scenario 5: Auto-cleanup"""
    print_step("SCENARIO 5", "Auto-cleanup During Low Load")
    
    print("1. Current system status...")
    initial_status = get_status()
    print_status(initial_status, "Initial ")
    
    print("\n2. Simulating low load period (30 seconds)...")
    print("   System should clean up unused containers...")
    
    # Monitor for cleanup
    for i in range(6):
        time.sleep(5)
        status = get_status()
        elapsed = (i + 1) * 5
        print(f"   T+{elapsed:2d}s: {status['total_containers']} containers, {status['total_load']} load")
    
    final_status = get_status()
    print_status(final_status, "After Cleanup ")

def run_full_demo():
    """Run the complete demo"""
    print_header("CONTAINER AUTO-SCALING SYSTEM DEMO")
    
    print("🎯 This demo will show:")
    print("   • Basic system operation")
    print("   • Auto-scaling under load")
    print("   • Load balancing")
    print("   • Real-time graph data")
    print("   • Auto-cleanup during low load")
    
    input("\n⏸️  Press Enter to start the demo...")
    
    try:
        # Test if system is running
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ System is not running!")
            print("Please start with: docker-compose up -d")
            return
    except Exception as e:
        print("❌ Cannot connect to system!")
        print("Please start with: docker-compose up -d")
        return
    
    # Run demo scenarios
    demo_scenario_1_basic_operation()
    input("\n⏸️  Press Enter to continue to auto-scaling demo...")
    
    demo_scenario_2_auto_scaling()
    input("\n⏸️  Press Enter to continue to load balancing demo...")
    
    demo_scenario_3_load_balancing()
    input("\n⏸️  Press Enter to continue to graph data demo...")
    
    demo_scenario_4_graph_data()
    input("\n⏸️  Press Enter to continue to auto-cleanup demo...")
    
    demo_scenario_5_auto_cleanup()
    
    print_header("DEMO COMPLETE")
    print("🎉 All demo scenarios completed successfully!")
    print("\n📊 Key Features Demonstrated:")
    print("   ✅ Dynamic container creation")
    print("   ✅ Auto-scaling based on load")
    print("   ✅ Load balancing across containers")
    print("   ✅ Real-time monitoring")
    print("   ✅ Auto-cleanup during low load")
    print("   ✅ Graph data for visualization")
    
    print("\n🌐 Next: Open the frontend web app to see live visualization!")
    print("   URL: http://localhost:3000")

if __name__ == "__main__":
    run_full_demo()
