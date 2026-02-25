import os
import requests
import json

api_key = os.getenv("SIMMER_API_KEY")
headers = {"Authorization": f"Bearer {api_key}"}
base_url = "https://api.simmer.markets/api/sdk"

def get_markets(query=None):
    params = {"status": "active", "limit": 50}
    if query:
        params["q"] = query
    response = requests.get(f"{base_url}/markets", headers=headers, params=params)
    return response.json()

def dry_run_price(market_id, side):
    payload = {
        "market_id": market_id,
        "side": side,
        "amount": 1.0,
        "dry_run": True,
        "venue": "simmer" # Defaulting to simmer for check, but should use the venue of the market
    }
    response = requests.post(f"{base_url}/trade", headers=headers, json=payload)
    data = response.json()
    if 'shares_bought' in data and data['shares_bought'] > 0:
        return 1.0 / data['shares_bought']
    return None

# Search for BTC and ETH sprint-like markets
all_response = get_markets()
all_markets = all_response if isinstance(all_response, list) else all_response.get('markets', [])

for market in all_markets:
    q = market['question']
    if ("Bitcoin Up or Down" in q) and ("February 17" in q):
        print(json.dumps(market, indent=2))
        break
