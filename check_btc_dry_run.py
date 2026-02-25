import os
import requests
import json

API_KEY = "sk_live_67cde9c17d16218b380e3452a7dbd4d5711b4a1a3c59a58e3d838aa93248a1b0"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
BASE_URL = "https://api.simmer.markets/api/sdk"

# BTC market
market_id = "2b2ea15d-62fd-4166-97ee-e3c898c0aa77"

res_yes = requests.post(f"{BASE_URL}/trade", headers=HEADERS, json={
    "market_id": market_id, "side": "yes", "amount": 10.0, "dry_run": True, "venue": "polymarket"
}).json()

print("YES Dry Run:")
print(json.dumps(res_yes, indent=2))

res_no = requests.post(f"{BASE_URL}/trade", headers=HEADERS, json={
    "market_id": market_id, "side": "no", "amount": 10.0, "dry_run": True, "venue": "polymarket"
}).json()

print("\nNO Dry Run:")
print(json.dumps(res_no, indent=2))
