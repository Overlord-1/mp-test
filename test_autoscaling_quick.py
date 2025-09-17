#!/usr/bin/env python3
import requests
import threading
import time

def send_request(i):
    try:
        response = requests.post('http://localhost:8000/work', json={'intensity': 5})
        if response.status_code == 200:
            result = response.json()
            print(f"Request {i+1}: Container {result.get('container_id', 'failed')[:12]}...")
        else:
            print(f"Request {i+1}: Failed - {response.status_code}")
    except Exception as e:
        print(f"Request {i+1}: Error - {e}")

# Send 3 concurrent requests
print("Sending 3 concurrent requests to test auto-scaling...")
threads = []
for i in range(3):
    thread = threading.Thread(target=send_request, args=(i,))
    threads.append(thread)
    thread.start()
    time.sleep(0.5)

# Wait for all to complete
for thread in threads:
    thread.join()

time.sleep(2)
print("\nChecking final status...")
response = requests.get('http://localhost:8000/status')
if response.status_code == 200:
    status = response.json()
    print(f"Total containers: {status['total_containers']}")
    print(f"Total load: {status['total_load']}")
    for container_id, info in status['containers'].items():
        print(f"  - {info['name']}: Load {info['load']}")
