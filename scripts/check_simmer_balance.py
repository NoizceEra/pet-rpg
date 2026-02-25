import os
import requests
SIMMER_API_KEY = os.getenv("SIMMER_API_KEY")
url = "https://api.simmer.markets/api/sdk/trades/batch"
headers = {"Authorization": f"Bearer {SIMMER_API_KEY}", "Content-Type": "application/json"}
payload = {
    "trades": [
        {"market_id": "test", "side": "yes", "amount": 0.01}
    ],
    "venue": "polymarket"
}
resp = requests.post(url, headers=headers, json=payload)
print(f"Status: {resp.status_code}")
print(resp.json())
