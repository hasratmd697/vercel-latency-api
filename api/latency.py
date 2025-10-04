import os
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# 1. Initialize the FastAPI app
app = FastAPI()

# 2. Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Load the data using a robust file path
# CHANGE #2: Use os.path.join to create a reliable path to the data file.
script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, 'q-vercel-latency.json')

try:
    df = pd.read_json(file_path)
except Exception as e:
    df = pd.DataFrame()
    print(f"Could not load data file: {e}")

# 4. Define the structure of the incoming POST request data
class RequestData(BaseModel):
    regions: List[str]
    threshold_ms: int

# 5. Create the API endpoint
# CHANGE #1: The path should be "/" because Vercel handles the "/api/latency" part.
@app.post("/")
def get_latency_metrics(data: RequestData):
    results = {}
    
    if df.empty:
        return {"error": "Data file not loaded or is empty."}

    for region in data.regions:
        region_df = df[df['region'] == region]

        if region_df.empty:
            results[region] = {"error": "No data available for this region"}
            continue

        # Calculate metrics
        avg_latency = region_df['latency_ms'].mean()
        p95_latency = region_df['latency_ms'].quantile(0.95)
        
        # CHANGE #3: Use the correct column name 'uptime_ms'.
        avg_uptime = region_df['uptime_ms'].mean() 
        
        breaches = (region_df['latency_ms'] > data.threshold_ms).sum()

        results[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": int(breaches)
        }

    return results