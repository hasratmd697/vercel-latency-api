import json
import random
from datetime import datetime, timedelta

# Generate sample telemetry data for different regions
regions = ["apac", "emea", "us-east", "us-west"]
sample_data = []

# Generate data for the last 24 hours
start_time = datetime.now() - timedelta(hours=24)

for i in range(1000):  # 1000 data points
    timestamp = start_time + timedelta(minutes=i * 1.44)  # ~1000 points over 24 hours
    
    for region in regions:
        # Different latency characteristics per region
        base_latency = {
            "apac": 120,
            "emea": 85,
            "us-east": 45,
            "us-west": 65
        }
        
        # Add some randomness and occasional spikes
        if random.random() < 0.05:  # 5% chance of spike
            latency = base_latency[region] + random.uniform(100, 300)
        else:
            latency = base_latency[region] + random.uniform(-20, 40)
        
        # Uptime (mostly high, occasional outages)
        uptime = 1.0 if random.random() > 0.02 else 0.0  # 2% downtime
        
        sample_data.append({
            "timestamp": timestamp.isoformat(),
            "region": region,
            "latency_ms": max(10, latency),  # Minimum 10ms
            "uptime": uptime
        })

# Save to file
with open('/Users/aig/Desktop/eshop-telemetry-api/sample_telemetry.json', 'w') as f:
    json.dump(sample_data, f, indent=2)

print(f"Generated {len(sample_data)} telemetry records")
print("Sample records:")
for i in range(3):
    print(f"  {sample_data[i]}")
