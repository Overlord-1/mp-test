#!/usr/bin/env python3
import requests
import threading
import time

def send_high_intensity_request(i):
    try:
        response = requests.post('http://localhost:8000/work', json={'intensity': 10})
        if response.status_code == 200:
            result = response.json()
            print(f"High intensity request {i+1}: Container {result.get('container_id', 'failed')[:12]}...")
            print(f"  Time taken: {result.get('time_taken', 0):.2f}s")
        else:
            print(f"High intensity request {i+1}: Failed - {response.status_code}")
    except Exception as e:
        print(f"High intensity request {i+1}: Error - {e}")

# Send 4 high-intensity concurrent requests
print("Sending 4 high-intensity concurrent requests to trigger auto-scaling...")
threads = []
for i in range(100):
    thread = threading.Thread(target=send_high_intensity_request, args=(i,))
    threads.append(thread)
    thread.start()
    time.sleep(0.3)  # Small delay between starting threads

# Wait for all to complete
for thread in threads:
    thread.join()

time.sleep(3)
print("\nChecking final status...")
response = requests.get('http://localhost:8000/status')
if response.status_code == 200:
    status = response.json()
    print(f"Total containers: {status['total_containers']}")
    print(f"Total load: {status['total_load']}")
    for container_id, info in status['containers'].items():
        print(f"  - {info['name']}: Load {info['load']}, Port {info['port']}")
