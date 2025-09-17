#!/usr/bin/env python3
"""
Quick test script to verify frontend connectivity
"""

import requests
import time

def test_backend():
    """Test backend connectivity"""
    print("🔧 Testing Backend Connectivity...")
    
    try:
        # Test health endpoint
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend health check: OK")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False
    
    try:
        # Test status endpoint
        response = requests.get('http://localhost:8000/status', timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Status endpoint: {status['total_containers']} containers, {status['total_load']} load")
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status endpoint failed: {e}")
        return False
    
    try:
        # Test graph endpoint
        response = requests.get('http://localhost:8000/graph', timeout=5)
        if response.status_code == 200:
            graph = response.json()
            print(f"✅ Graph endpoint: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")
        else:
            print(f"❌ Graph endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Graph endpoint failed: {e}")
        return False
    
    return True

def create_test_container():
    """Create a test container"""
    print("\n🚀 Creating Test Container...")
    
    try:
        response = requests.post('http://localhost:8000/work', 
                               json={'intensity': 3}, 
                               timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Container created: {result['container_id'][:12]}...")
            print(f"   Time taken: {result['time_taken']:.2f}s")
            return True
        else:
            print(f"❌ Container creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Container creation failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Frontend Connectivity Test")
    print("=" * 40)
    
    # Test backend
    if not test_backend():
        print("\n❌ Backend tests failed. Please check:")
        print("   1. Is docker-compose running? (docker-compose up -d)")
        print("   2. Are containers healthy? (docker ps)")
        return
    
    # Create test container
    if create_test_container():
        print("\n✅ Test container created successfully!")
    else:
        print("\n⚠️  Test container creation failed, but backend is working")
    
    print("\n🌐 Frontend should now work at: http://localhost:3000")
    print("📊 You should see:")
    print("   - Connected status (green dot)")
    print("   - Container count > 0")
    print("   - Graph nodes visible")
    print("   - Activity logs in the right panel")
    
    print("\n🔍 To view live logs, run: python view_logs.py")

if __name__ == "__main__":
    main()
