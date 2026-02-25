import os
import requests
import json
import re

API_KEY = os.environ.get("SIMMER_API_KEY")
BASE_URL = "https://api.simmer.markets/api/sdk"
CLOB_URL = "https://clob.polymarket.com/book"

def get_best_ask(token_id):
    try:
        response = requests.get(CLOB_URL, params={"token_id": token_id})
        data = response.json()
        asks = data.get("asks", [])
        if asks:
            return min(float(ask["price"]) for ask in asks)
    except: pass
    return None

headers = {"Authorization": f"Bearer {API_KEY}"}
params = {"status": "active", "limit": 200}
markets = requests.get(f"{BASE_URL}/markets", headers=headers, params=params).json().get("markets", [])

print("Scanning for ALL BTC/ETH sprint markets...")
found_any = False
for m in markets:
    q = m["question"]
    if "Bitcoin Up or Down" not in q and "Ethereum Up or Down" not in q:
        continue
    
    y = get_best_ask(m.get('polymarket_token_id'))
    n = get_best_ask(m.get('polymarket_no_token_id'))
    if y and n:
        total = y + n
        print(f"Checking {q}: {total:.4f}")
        if total < 0.99: # 1% edge
            found_any = True
            print(f"💰 ARB DETECTED! {q}")
            print(f"  YES: {y:.3f}, NO: {n:.3f} | Total: {total:.4f} | Edge: {1.0 - total:.4f}")
            print("  Attempting Execution...")
            payload = {
                "trades": [
                    {"market_id": m["id"], "side": "yes", "amount": 25.0},
                    {"market_id": m["id"], "side": "no", "amount": 25.0}
                ],
                "venue": "polymarket",
                "source": "sdk:micro-arb",
                "reasoning": f"@PBot1 Micro-Arb: Combined cost {total:.4f} < $1.00. Executing $50 total."
            }
            resp = requests.post(f"{BASE_URL}/trades/batch", headers=headers, json=payload)
            print(f"  Result: {resp.status_code} - {resp.text}")
    else:
        print(f"Skipping {q} (No Liquidity)")
    
if not found_any:
    print("No micro-arbitrage opportunities found in 200 markets.")
