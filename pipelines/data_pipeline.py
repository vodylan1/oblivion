"""
data_pipeline.py

DATA_PIPELINE module.
In Phase 2, we'll fetch a simple price feed from an external API
(or use mock data if you prefer). This data will later expand
to more advanced feeds (orderbooks, socials, whales, etc.).
"""

import requests
import time

def data_pipeline_init():
    """
    Initialize any needed configurations or API keys (placeholder).
    """
    print("[DataPipeline] Initialized.")

def fetch_sol_price():
    """
    Fetch current Solana price from CoinGecko (as an example).
    Return a dict with relevant data.
    If real calls are undesirable, just mock the data.
    """
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "solana",
            "vs_currencies": "usd"
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        # Example: {'solana': {'usd': 19.52}}
        sol_price = data.get("solana", {}).get("usd", 0.0)

        return {
            "sol_price": sol_price,
            "timestamp": time.time()
        }

    except Exception as e:
        print(f"[DataPipeline] Error fetching SOL price: {e}")
        # Return a fallback or mock data
        return {
            "sol_price": 999.99,  # placeholder fallback
            "timestamp": time.time()
        }
