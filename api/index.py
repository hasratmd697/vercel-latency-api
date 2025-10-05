from http.server import BaseHTTPRequestHandler
import json
import os
from typing import List, Dict, Any

class TelemetryHandler(BaseHTTPRequestHandler):
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
            telemetry_data = self.load_telemetry_data()
            
            if not telemetry_data:
                self.wfile.write(json.dumps({'error': 'No telemetry data available'}).encode())
                return
            
            # Calculate metrics for each region
            results = {}
            for region in regions:
                metrics = self.calculate_region_metrics(telemetry_data, region, threshold_ms)
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

    def load_telemetry_data(self) -> List[Dict[str, Any]]:
        """Load telemetry data from JSON file"""
        # Try different possible paths
        possible_paths = [
            "sample_telemetry.json",  # Same directory
            "/var/task/sample_telemetry.json",  # Vercel deployment path
            "../sample_telemetry.json",  # One level up
            "/tmp/sample_telemetry.json",  # Temp directory
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return json.load(f)
        
        # Return empty list if no file found
        return []

    def calculate_percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile without external dependencies"""
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

    def calculate_region_metrics(self, data: List[Dict[str, Any]], region: str, threshold_ms: float) -> Dict[str, float]:
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
        p95_latency = self.calculate_percentile(latencies, 95)
        avg_uptime = sum(uptimes) / len(uptimes)
        breaches = sum(1 for latency in latencies if latency > threshold_ms)
        
        return {
            'avg_latency': round(avg_latency, 2),
            'p95_latency': round(p95_latency, 2),
            'avg_uptime': round(avg_uptime, 4),
            'breaches': breaches
        }

def handler(request, response):
    """Vercel serverless function handler"""
    # Create a mock request object for the handler
    class MockRequest:
        def __init__(self, method, path, headers, body):
            self.method = method
            self.path = path
            self.headers = headers
            self.body = body
    
    # Process the request
    telemetry_handler = TelemetryHandler()
    
    if request.method == 'OPTIONS':
        response.status_code = 200
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return
    
    if request.method == 'POST':
        try:
            request_data = request.json
            
            if 'regions' not in request_data or 'threshold_ms' not in request_data:
                response.status_code = 400
                return {'error': 'Missing regions or threshold_ms'}
            
            regions = request_data['regions']
            threshold_ms = request_data['threshold_ms']
            
            # Load telemetry data
            telemetry_data = telemetry_handler.load_telemetry_data()
            
            if not telemetry_data:
                response.status_code = 500
                return {'error': 'No telemetry data available'}
            
            # Calculate metrics for each region
            results = {}
            for region in regions:
                metrics = telemetry_handler.calculate_region_metrics(telemetry_data, region, threshold_ms)
                results[region] = metrics
            
            response.headers['Access-Control-Allow-Origin'] = '*'
            return results
            
        except Exception as e:
            response.status_code = 500
            response.headers['Access-Control-Allow-Origin'] = '*'
            return {'error': str(e)}
    
    if request.method == 'GET':
        response.headers['Access-Control-Allow-Origin'] = '*'
        return {'message': 'eShop Telemetry API is running'}
    
    response.status_code = 405
    return {'error': 'Method not allowed'}
