#!/usr/bin/env python3

import requests
import json
import subprocess
import time
import threading
import sys

def start_server():
    """Start the FastAPI server in background"""
    try:
        subprocess.run(["python3", "-m", "uvicorn", "api.telemetry:app", "--host", "0.0.0.0", "--port", "8000"], 
                      cwd="/Users/aig/Desktop/eshop-telemetry-api", check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")

def test_endpoint():
    """Test the telemetry endpoint"""
    base_url = "http://localhost:8000"
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/")
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test telemetry endpoint with the sample data from requirements
    test_payload = {
        "regions": ["apac", "emea"],
        "threshold_ms": 150
    }
    
    try:
        response = requests.post(f"{base_url}/api/telemetry", json=test_payload)
        print(f"\nTelemetry test: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Response:")
            print(json.dumps(result, indent=2))
            
            # Validate response structure
            for region in test_payload["regions"]:
                if region in result:
                    metrics = result[region]
                    expected_keys = ["avg_latency", "p95_latency", "avg_uptime", "breaches"]
                    if all(key in metrics for key in expected_keys):
                        print(f"✅ {region}: All required metrics present")
                    else:
                        print(f"❌ {region}: Missing metrics")
                else:
                    print(f"❌ {region}: Not in response")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Telemetry test failed: {e}")

if __name__ == "__main__":
    print("Testing eShop Telemetry API...")
    
    # Start server in background thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Run tests
    test_endpoint()
    
    print("\nTest completed. Press Ctrl+C to stop the server.")
