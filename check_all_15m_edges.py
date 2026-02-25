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

found = []
for m in markets:
    q = m["question"]
    if "Bitcoin Up or Down" not in q and "Ethereum Up or Down" not in q:
        continue
    
    match = re.search(r'(\d+):(\d+)(AM|PM)\s*-\s*(\d+):(\d+)(AM|PM)', q)
    if match:
        h1, m1, p1, h2, m2, p2 = match.groups()
        if (int(m2) - int(m1)) % 60 == 15:
            y = get_best_ask(m.get('polymarket_token_id'))
            n = get_best_ask(m.get('polymarket_no_token_id'))
            if y and n:
                total = y + n
                edge = 1.0 - total
                found.append({"q": q, "total": total, "edge": edge, "y": y, "n": n})

# Sort by edge descending
found.sort(key=lambda x: x["edge"], reverse=True)

for f in found:
    print(f"{f['q']} | Total: {f['total']:.4f} | Edge: {f['edge']:.4f} | Y: {f['y']:.3f} N: {f['n']:.3f}")
