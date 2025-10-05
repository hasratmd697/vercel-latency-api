from http.server import BaseHTTPRequestHandler
import json
import os
from typing import List, Dict, Any

def load_telemetry_data() -> List[Dict[str, Any]]:
    """Load telemetry data from JSON file"""
    # Try different possible paths for Vercel deployment
    possible_paths = [
        "api/sample_telemetry.json",  # Relative to project root
        "sample_telemetry.json",      # Same directory
        "/var/task/api/sample_telemetry.json",  # Vercel task path
        "/tmp/sample_telemetry.json", # Temp directory
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
    
    # Return empty list if no file found
    return []

def calculate_percentile(values: List[float], percentile: float) -> float:
    """Calculate percentile without numpy"""
    if not values:
        return 0.0
    
    sorted_values = sorted(values)
    n = len(sorted_values)
    index = (percentile / 100) * (n - 1)
    
    if index == int(index):
        return sorted_values[int(index)]
    else:
        lower_index = int(index)
        upper_index = lower_index + 1
        if upper_index >= n:
            return sorted_values[-1]
        
        weight = index - lower_index
        return sorted_values[lower_index] + weight * (sorted_values[upper_index] - sorted_values[lower_index])

def calculate_region_metrics(data: List[Dict[str, Any]], region: str, threshold_ms: float) -> Dict[str, float]:
    """Calculate metrics for a specific region"""
    # Filter data for the specific region
    region_data = [record for record in data if record.get('region') == region]
    
    if not region_data:
        return {
            'avg_latency': 0.0,
            'p95_latency': 0.0,
            'avg_uptime': 0.0,
            'breaches': 0
        }
    
    # Extract latencies and uptime values
    latencies = [record['latency_ms'] for record in region_data]
    uptimes = [record['uptime'] for record in region_data]
    
    # Calculate metrics
    avg_latency = sum(latencies) / len(latencies)
    p95_latency = calculate_percentile(latencies, 95)
    avg_uptime = sum(uptimes) / len(uptimes)
    breaches = sum(1 for latency in latencies if latency > threshold_ms)
    
    return {
        'avg_latency': round(avg_latency, 2),
        'p95_latency': round(p95_latency, 2),
        'avg_uptime': round(avg_uptime, 4),
        'breaches': breaches
    }

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """Handle POST requests for telemetry analysis"""
        try:
            # Set CORS headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Validate request
            if 'regions' not in request_data or 'threshold_ms' not in request_data:
                self.wfile.write(json.dumps({'error': 'Missing regions or threshold_ms'}).encode())
                return
            
            regions = request_data['regions']
            threshold_ms = request_data['threshold_ms']
            
            # Load telemetry data
            telemetry_data = load_telemetry_data()
            
            if not telemetry_data:
                self.wfile.write(json.dumps({'error': 'No telemetry data available'}).encode())
                return
            
            # Calculate metrics for each region
            results = {}
            for region in regions:
                metrics = calculate_region_metrics(telemetry_data, region, threshold_ms)
                results[region] = metrics
            
            # Send response
            self.wfile.write(json.dumps(results).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def do_GET(self):
        """Handle GET requests for health check"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'message': 'eShop Telemetry API is running'}).encode())
