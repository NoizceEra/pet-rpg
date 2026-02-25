import os
import requests
import json

API_KEY = os.environ.get("SIMMER_API_KEY")
BASE_URL = "https://api.simmer.markets/api/sdk"

market_id = "fd4a8b33-1706-4157-afc5-aed1df92013d" # Ethereum 5:30-5:45
trade_size = 50.0

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# Check prices one last time via dry run to confirm edge
payload_dry = {
    "market_id": market_id,
    "side": "yes",
    "amount": 25.0,
    "dry_run": True,
    "venue": "polymarket"
}
y_res = requests.post(f"{BASE_URL}/trade", headers=headers, json=payload_dry).json()

payload_dry["side"] = "no"
n_res = requests.post(f"{BASE_URL}/trade", headers=headers, json=payload_dry).json()

if y_res.get("success") and n_res.get("success"):
    y_price = 25.0 / y_res["shares_bought"]
    n_price = 25.0 / n_res["shares_bought"]
    total = y_price + n_price
    print(f"Final check: YES {y_price:.3f}, NO {n_price:.3f} | Total {total:.4f}")
    
    if total < 1.0:
        print("Executing arbitrage trade...")
        payload = {
            "trades": [
                {"market_id": market_id, "side": "yes", "amount": 25.0},
                {"market_id": market_id, "side": "no", "amount": 25.0}
            ],
            "venue": "polymarket",
            "source": "sdk:micro-arb",
            "reasoning": f"@PBot1 Micro-Arb: Combined cost {total:.4f} < $1.00. Executing $50 total."
        }
        resp = requests.post(f"{BASE_URL}/trades/batch", headers=headers, json=payload)
        print(f"Result: {resp.status_code} - {resp.text}")
    else:
        print("Edge vanished. Skipping.")
else:
    print("Failed to get dry run.")
