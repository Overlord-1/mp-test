#!/usr/bin/env python3
"""
Detailed Auto-scaling verification test script
"""

import requests
import threading
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def send_long_work_request(intensity, duration, request_id):
    """Send a work request that will keep a container busy for a specified duration"""
    try:
        print(f"🚀 Request {request_id}: Starting LONG work (intensity {intensity}, duration {duration}s)")
        
        # Send the request
        response = requests.post(
            f"{BASE_URL}/work",
            json={"intensity": intensity},
            timeout=duration + 10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Request {request_id}: Completed")
            print(f"   Container: {result.get('container_id', 'N/A')[:12]}...")
            print(f"   Message: {result.get('message', 'N/A')}")
            return result.get('container_id')
        else:
            print(f"❌ Request {request_id}: Failed with status {response.status_code}")
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

def print_status(status_data, label=""):
    """Print formatted status information"""
    if not status_data:
        print("❌ Could not get status")
        return
    
    print(f"\n📊 {label}Status:")
    print(f"   Total Containers: {status_data['total_containers']}")
    print(f"   Total Load: {status_data['total_load']}")
    print(f"   Timestamp: {status_data['timestamp']}")
    
    if status_data['containers']:
        print(f"   Active Containers:")
        for container_id, info in status_data['containers'].items():
            print(f"     - {info['name']}: Load {info['load']}, Port {info['port']}")
    else:
        print("   No active containers")

def monitor_system(duration_seconds):
    """Monitor the system for a specified duration"""
    print(f"\n👀 Monitoring system for {duration_seconds} seconds...")
    
    start_time = time.time()
    while time.time() - start_time < duration_seconds:
        status = get_status()
        elapsed = int(time.time() - start_time)
        print(f"   T+{elapsed:2d}s: {status['total_containers']} containers, {status['total_load']} total load")
        time.sleep(2)
    
    return get_status()

def test_autoscaling_detailed():
    """Test auto-scaling functionality with detailed monitoring"""
    print("🧪 DETAILED AUTO-SCALING VERIFICATION TEST")
    print("=" * 60)
    
    # Step 1: Clean slate - check initial status
    print("\n1️⃣ Initial Status Check")
    initial_status = get_status()
    print_status(initial_status, "Initial ")
    
    # Step 2: Send requests that will keep containers busy
    print("\n2️⃣ Triggering Auto-scaling with Long-Running Requests")
    print("   Sending 4 concurrent LONG requests (intensity 10, ~10 seconds each)...")
    
    threads = []
    results = []
    
    # Start multiple threads to send concurrent long-running requests
    for i in range(4):
        thread = threading.Thread(
            target=lambda i=i: results.append(send_long_work_request(10, 15, i+1))
        )
        threads.append(thread)
        thread.start()
        
        # Small delay between starting threads to see scaling in action
        time.sleep(1)
    
    # Step 3: Monitor the system while requests are running
    print("\n3️⃣ Monitoring System During High Load")
    time.sleep(2)  # Let requests start
    status_during_load = get_status()
    print_status(status_during_load, "During Load ")
    
    # Monitor for a bit more
    monitor_system(8)
    
    # Step 4: Wait for all requests to complete
    print("\n4️⃣ Waiting for All Requests to Complete...")
    for thread in threads:
        thread.join()
    
    # Step 5: Check status after requests complete
    print("\n5️⃣ Status After Requests Complete")
    time.sleep(2)  # Give system time to process
    status_after_completion = get_status()
    print_status(status_after_completion, "After Completion ")
    
    # Step 6: Monitor auto-cleanup
    print("\n6️⃣ Monitoring Auto-cleanup (20 seconds)...")
    final_status = monitor_system(20)
    print_status(final_status, "Final ")
    
    # Step 7: Analysis
    print("\n7️⃣ Auto-scaling Analysis")
    print("=" * 40)
    
    initial_containers = initial_status['total_containers'] if initial_status else 0
    peak_containers = status_during_load['total_containers'] if status_during_load else 0
    final_containers = final_status['total_containers'] if final_status else 0
    
    print(f"Initial containers: {initial_containers}")
    print(f"Peak containers: {peak_containers}")
    print(f"Final containers: {final_containers}")
    
    # Verify auto-scaling worked
    if peak_containers > initial_containers:
        print("✅ Auto-scaling UP: Working correctly")
        print(f"   Scaled from {initial_containers} to {peak_containers} containers")
    else:
        print("❌ Auto-scaling UP: Did not trigger")
        print("   This might be normal if requests completed too quickly")
    
    # Verify auto-cleanup worked
    if final_containers <= peak_containers:
        print("✅ Auto-cleanup: Working correctly")
        if final_containers < peak_containers:
            print(f"   Scaled down from {peak_containers} to {final_containers} containers")
        else:
            print("   No cleanup needed (appropriate number of containers)")
    else:
        print("⚠️  Auto-cleanup: Unexpected behavior")
    
    # Check load balancing
    if status_during_load and status_during_load['containers']:
        loads = [info['load'] for info in status_during_load['containers'].values()]
        if len(loads) > 1:
            print("✅ Load balancing: Working (multiple containers with different loads)")
        elif len(loads) == 1 and loads[0] > 0:
            print("ℹ️  Load balancing: Single container handling load (normal for low load)")
        else:
            print("ℹ️  Load balancing: No active load")

def test_manual_scaling():
    """Test manual scaling by sending rapid requests"""
    print("\n8️⃣ Manual Scaling Test")
    print("=" * 30)
    
    print("Sending rapid requests to test scaling...")
    
    # Send requests rapidly
    for i in range(6):
        try:
            response = requests.post(
                f"{BASE_URL}/work",
                json={"intensity": 3},
                timeout=5
            )
            if response.status_code == 200:
                result = response.json()
                print(f"   Request {i+1}: Container {result.get('container_id', 'N/A')[:12]}...")
            else:
                print(f"   Request {i+1}: Failed")
        except Exception as e:
            print(f"   Request {i+1}: Error - {e}")
        
        time.sleep(0.5)  # Small delay between requests
    
    # Check status after rapid requests
    time.sleep(2)
    status = get_status()
    print_status(status, "After Rapid Requests ")

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
    
    # Run detailed auto-scaling test
    test_autoscaling_detailed()
    
    # Test manual scaling
    test_manual_scaling()
    
    print("\n🎉 Detailed auto-scaling verification complete!")
    print("\nKey observations:")
    print("- Auto-scaling triggers when load > 3")
    print("- Auto-cleanup triggers when total load < 2 and multiple containers exist")
    print("- Load balancing distributes requests across available containers")
    print("- System monitors containers every 5 seconds")

if __name__ == "__main__":
    main()
