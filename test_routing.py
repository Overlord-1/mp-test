#!/usr/bin/env python3
"""
Test script for the routing server
"""

import requests
import time
import json
import threading

BASE_URL = "http://localhost:8000"

def test_work_endpoint():
    """Test the /work endpoint"""
    print("Testing /work endpoint...")
    
    # Test with different intensities
    for intensity in [1, 3, 5]:
        print(f"Sending work request with intensity {intensity}")
        response = requests.post(
            f"{BASE_URL}/work",
            json={"intensity": intensity}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Success: {result['message']}")
            print(f"  Time taken: {result['time_taken']:.2f}s")
            print(f"  Container: {result.get('container_id', 'N/A')}")
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
        print()

def test_status_endpoint():
    """Test the /status endpoint"""
    print("Testing /status endpoint...")
    
    response = requests.get(f"{BASE_URL}/status")
    
    if response.status_code == 200:
        status = response.json()
        print(f"✓ Status retrieved successfully")
        print(f"  Total containers: {status['total_containers']}")
        print(f"  Total load: {status['total_load']}")
        
        if status['containers']:
            print("  Active containers:")
            for container_id, info in status['containers'].items():
                print(f"    - {info['name']}: port {info['port']}, load {info['load']}")
        else:
            print("  No active containers")
    else:
        print(f"✗ Error: {response.status_code} - {response.text}")
    print()

def test_graph_endpoint():
    """Test the /graph endpoint"""
    print("Testing /graph endpoint...")
    
    response = requests.get(f"{BASE_URL}/graph")
    
    if response.status_code == 200:
        graph_data = response.json()
        print(f"✓ Graph data retrieved successfully")
        print(f"  Nodes: {len(graph_data['nodes'])}")
        print(f"  Edges: {len(graph_data['edges'])}")
        print(f"  Total containers: {graph_data['total_containers']}")
        print(f"  Total load: {graph_data['total_load']}")
        
        # Test the transformApiResponse function
        elements = transformApiResponse(graph_data)
        print(f"  Transformed elements: {len(elements['elements'])}")
    else:
        print(f"✗ Error: {response.status_code} - {response.text}")
    print()

def test_health_endpoint():
    """Test the /health endpoint"""
    print("Testing /health endpoint...")
    
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        health = response.json()
        print(f"✓ Health check passed: {health['status']}")
    else:
        print(f"✗ Error: {response.status_code} - {response.text}")
    print()

def test_load_scaling():
    """Test container scaling under load"""
    print("Testing container scaling...")
    
    def send_request(intensity):
        response = requests.post(
            f"{BASE_URL}/work",
            json={"intensity": intensity}
        )
        if response.status_code == 200:
            result = response.json()
            print(f"  Request {intensity}: {result.get('container_id', 'N/A')}")
        else:
            print(f"  Request {intensity} failed: {response.status_code}")
    
    # Send multiple concurrent requests
    threads = []
    for i in range(5):
        thread = threading.Thread(target=send_request, args=(2,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print("  All requests completed")
    print()

def transformApiResponse(apiData):
    """Transform API response for frontend (same as provided by user)"""
    elements = []
    
    # Add nodes
    for node in apiData['nodes']:
        node_type = 'healthy' if node['color'] == 'green' else 'warning' if node['color'] == 'yellow' else 'danger'
        elements.append({
            'data': { 
                'id': node['id'], 
                'label': node['label'], 
                'type': node_type
            }
        })
    
    # Add edges
    for edge in apiData['edges']:
        elements.append({
            'data': { 
                'source': edge['source'], 
                'target': edge['target'] 
            }
        })
    
    return {'elements': elements}

def main():
    """Run all tests"""
    print("=" * 50)
    print("ROUTING SERVER TEST SUITE")
    print("=" * 50)
    print()
    
    try:
        # Test health first
        test_health_endpoint()
        
        # Test initial status (should be empty)
        test_status_endpoint()
        
        # Test work endpoint
        test_work_endpoint()
        
        # Test status after work
        test_status_endpoint()
        
        # Test graph endpoint
        test_graph_endpoint()
        
        # Test load scaling
        test_load_scaling()
        
        # Final status check
        test_status_endpoint()
        
        print("=" * 50)
        print("ALL TESTS COMPLETED")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to routing server")
        print("Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

if __name__ == "__main__":
    main()
