# /api/latency.py

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# 1. Initialize the FastAPI app
app = FastAPI()

# 2. Enable CORS
# This allows web pages from any domain to make requests to your API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# 3. Load the data into a pandas DataFrame
# This is done once when the app starts, which is efficient.
try:
    df = pd.read_json('api/q-vercel-latency.json')
except Exception as e:
    # If the file isn't found, create an empty DataFrame to avoid crashing
    df = pd.DataFrame()
    print(f"Could not load data file: {e}")

# 4. Define the structure of the incoming POST request data
# Pydantic models automatically validate the incoming data.
class RequestData(BaseModel):
    regions: List[str]
    threshold_ms: int

# 5. Create the API endpoint
@app.post("/api/latency")
def get_latency_metrics(data: RequestData):
    """
    This endpoint calculates latency metrics for specified regions.
    """
    results = {}
    
    # Check if the dataframe is empty
    if df.empty:
        return {"error": "Data file not loaded or is empty."}

    # 6. Loop through each region provided in the request
    for region in data.regions:
        # Filter the DataFrame to get data for the current region only
        region_df = df[df['region'] == region]

        # If there's no data for that region, skip it
        if region_df.empty:
            results[region] = {"error": "No data available for this region"}
            continue

        # 7. Calculate the required metrics using pandas
        avg_latency = region_df['latency_ms'].mean()
        p95_latency = region_df['latency_ms'].quantile(0.95)
        avg_uptime = region_df['uptime_percentage'].mean()
        
        # Count how many records are above the threshold
        breaches = (region_df['latency_ms'] > data.threshold_ms).sum()

        # 8. Store the calculated metrics in the results dictionary
        results[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": int(breaches) # Convert from numpy int to standard int
        }

    return results