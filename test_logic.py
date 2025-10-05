#!/usr/bin/env python3

import sys
import os
sys.path.append('/Users/aig/Desktop/eshop-telemetry-api')

from api.telemetry import app
import json

# Test the telemetry calculation directly
def test_telemetry_logic():
    print("Testing telemetry logic directly...")
    
    # Import the functions from our API
    from api.telemetry import load_telemetry_data, calculate_region_metrics
    
    # Load the sample data
    telemetry_data = load_telemetry_data()
    print(f"Loaded {len(telemetry_data)} telemetry records")
    
    if telemetry_data:
        # Show sample of data
        print("\nSample data points:")
        for i in range(min(3, len(telemetry_data))):
            print(f"  {telemetry_data[i]}")
        
        # Test with the required payload
        regions = ["apac", "emea"]
        threshold_ms = 150
        
        print(f"\nTesting with regions: {regions}, threshold: {threshold_ms}ms")
        
        for region in regions:
            metrics = calculate_region_metrics(telemetry_data, region, threshold_ms)
            print(f"\n{region.upper()} Metrics:")
            print(f"  avg_latency: {metrics.avg_latency}ms")
            print(f"  p95_latency: {metrics.p95_latency}ms")
            print(f"  avg_uptime: {metrics.avg_uptime}")
            print(f"  breaches: {metrics.breaches}")
        
        # Create the full response format
        results = {}
        for region in regions:
            metrics = calculate_region_metrics(telemetry_data, region, threshold_ms)
            results[region] = {
                "avg_latency": metrics.avg_latency,
                "p95_latency": metrics.p95_latency,
                "avg_uptime": metrics.avg_uptime,
                "breaches": metrics.breaches
            }
        
        print("\nFull API Response:")
        print(json.dumps(results, indent=2))
        
        return True
    else:
        print("No telemetry data found!")
        return False

if __name__ == "__main__":
    # Change to the correct directory
    os.chdir('/Users/aig/Desktop/eshop-telemetry-api')
    success = test_telemetry_logic()
    
    if success:
        print("\n✅ Telemetry logic test passed!")
    else:
        print("\n❌ Telemetry logic test failed!")
