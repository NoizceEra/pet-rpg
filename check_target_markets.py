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
params = {"status": "active", "limit": 100}
markets = requests.get(f"{BASE_URL}/markets", headers=headers, params=params).json().get("markets", [])

print("Scanning for 15-minute BTC/ETH markets...")
for m in markets:
    q = m["question"]
    if "Bitcoin Up or Down" not in q and "Ethereum Up or Down" not in q:
        continue
    
    match = re.search(r'(\d+):(\d+)(AM|PM)\s*-\s*(\d+):(\d+)(AM|PM)', q)
    if match:
        h1, m1, p1, h2, m2, p2 = match.groups()
        m1, m2 = int(m1), int(m2)
        if (m2 - m1) % 60 == 15:
            print(f"Checking {q}...")
            y = get_best_ask(m.get('polymarket_token_id'))
            n = get_best_ask(m.get('polymarket_no_token_id'))
            if y and n:
                total = y + n
                print(f"  YES: {y:.3f}, NO: {n:.3f} | Total: {total:.4f}")
                if total < 1.0:
                    print(f"  💰 ARB DETECTED! Edge: {1.0 - total:.4f}")
            else:
                print("  Could not get asks.")
