import os
import requests
import time

SIMMER_API_KEY = os.getenv("SIMMER_API_KEY")
SIMMER_BASE = "https://api.simmer.markets"

def liquidate_market(market_id, shares_yes, shares_no):
    url = f"{SIMMER_BASE}/api/sdk/trade"
    headers = {
        "Authorization": f"Bearer {SIMMER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    if shares_yes > 0:
        payload = {
            "market_id": market_id,
            "side": "yes",
            "venue": "polymarket",
            "action": "sell",
            "shares": shares_yes
        }
        resp = requests.post(url, json=payload, headers=headers)
        print(f"Sell YES Result: {resp.json()}")

    if shares_no > 0:
        payload = {
            "market_id": market_id,
            "side": "no",
            "venue": "polymarket",
            "action": "sell",
            "shares": shares_no
        }
        resp = requests.post(url, json=payload, headers=headers)
        print(f"Sell NO Result: {resp.json()}")

if __name__ == "__main__":
    # From get_all_positions.py output:
    # 8fbf3f69-0324-4ee0-b44d-d0227cf244cf
    # shares_yes: 15.0699, shares_no: 14.1153
    liquidate_market("8fbf3f69-0324-4ee0-b44d-d0227cf244cf", 15.0699, 14.1153)
