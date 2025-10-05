# eShop Telemetry API

A serverless API endpoint for analyzing telemetry data from eShopCo storefronts, deployed on Vercel.

## Overview

This API analyzes latency pings from various regions and provides metrics to help product managers monitor whether deployments stay under target latency thresholds.

## API Endpoint

### POST /api/telemetry

Analyzes telemetry data for specified regions and returns performance metrics.

**Request Body:**
```json
{
  "regions": ["apac", "emea"],
  "threshold_ms": 150
}
```

**Response:**
```json
{
  "apac": {
    "avg_latency": 139.07,
    "p95_latency": 159.95,
    "avg_uptime": 0.975,
    "breaches": 202
  },
  "emea": {
    "avg_latency": 104.5,
    "p95_latency": 124.81,
    "avg_uptime": 0.981,
    "breaches": 49
  }
}
```

**Response Fields:**
- `avg_latency`: Mean latency in milliseconds
- `p95_latency`: 95th percentile latency in milliseconds
- `avg_uptime`: Mean uptime (0.0 to 1.0)
- `breaches`: Count of records above the threshold

## Features

- ✅ Accepts POST requests with JSON body containing regions and threshold_ms
- ✅ Returns per-region metrics (avg_latency, p95_latency, avg_uptime, breaches)
- ✅ CORS enabled for POST requests from any origin
- ✅ Serverless deployment on Vercel
- ✅ No external dependencies for math calculations

## Available Regions

- `apac` - Asia Pacific
- `emea` - Europe, Middle East, Africa
- `us-east` - US East Coast
- `us-west` - US West Coast

## Deployment

### Deploy to Vercel

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Deploy:
   ```bash
   vercel --prod
   ```

### Local Development

1. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install fastapi uvicorn
   ```

3. Run server:
   ```bash
   python -m uvicorn api.telemetry:app --host 0.0.0.0 --port 8000
   ```

4. Test endpoint:
   ```bash
   curl -X POST http://localhost:8000/api/telemetry \
     -H "Content-Type: application/json" \
     -d '{"regions":["apac","emea"],"threshold_ms":150}'
   ```

## Testing

Run the included test script:
```bash
python test_logic.py
```

## Project Structure

```
eshop-telemetry-api/
├── api/
│   ├── telemetry.py          # Main FastAPI application
│   ├── index.py              # Alternative Vercel handler
│   └── sample_telemetry.json # Sample telemetry data
├── vercel.json               # Vercel configuration
├── requirements.txt          # Python dependencies
├── test_logic.py            # Logic testing script
├── generate_sample_data.py  # Data generation script
└── README.md                # This file
```

## Sample Data

The API uses generated sample telemetry data with realistic latency patterns:
- 4000 data points across 4 regions
- 24 hours of simulated data
- Realistic latency distributions per region
- Occasional latency spikes and downtime events

## CORS Configuration

The API is configured to accept requests from any origin with the following headers:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET, POST, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type`
# TDA-IITM-eShopCo
