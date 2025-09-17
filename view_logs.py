#!/usr/bin/env python3
"""
Log viewer for the container auto-scaling system
"""

import requests
import time
import json
from datetime import datetime

def get_logs():
    """Get logs from the routing server"""
    try:
        response = requests.get('http://localhost:8000/status')
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error getting logs: {e}")
        return None

def print_logs():
    """Print formatted logs"""
    print("=" * 80)
    print(f"📊 CONTAINER AUTO-SCALING SYSTEM LOGS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    status = get_logs()
    if not status:
        print("❌ Could not connect to backend")
        return
    
    print(f"🐳 Total Containers: {status['total_containers']}")
    print(f"⚖️  Total Load: {status['total_load']}")
    print(f"🕒 Last Update: {status['timestamp']}")
    print()
    
    if status['containers']:
        print("📋 Active Containers:")
        for container_id, info in status['containers'].items():
            color = "🟢" if info['load'] == 0 else "🟡" if info['load'] < 3 else "🔴"
            print(f"  {color} {info['name']}")
            print(f"     ID: {container_id[:12]}...")
            print(f"     Load: {info['load']}")
            print(f"     Port: {info['port']}")
            print(f"     Created: {info['created_at']}")
            print()
    else:
        print("📋 No active containers")
        print()

def main():
    """Main log viewer loop"""
    print("🔍 Container Auto-scaling System Log Viewer")
    print("Press Ctrl+C to exit")
    print()
    
    try:
        while True:
            print_logs()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n👋 Log viewer stopped")

if __name__ == "__main__":
    main()
