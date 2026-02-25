#!/usr/bin/env python3
"""Debug actual trade error response."""

import requests
import json

NEW_KEY = "sk_live_484943fcabd5d3dd5e58106872e6831aedbd340139736760dc10773c47471570"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {NEW_KEY}"}

print("\n[Getting sample market]")

r = requests.get(f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=10", 
                headers=headers, timeout=5)
markets = r.json().get('markets', [])

market = None
for m in markets:
    if m.get('current_price'):
        market = m
        break

if market:
    print(f"Market: {market.get('question')}")
    print(f"Market ID: {market['id']}")
    print(f"Current Price: {market.get('current_price')}")
    
    print("\n[Attempting trade]")
    payload = {
        "market_id": market['id'],
        "side": "yes",
        "amount_usd": 0.50,
    }
    
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    r = requests.post(f"{SIMMER_BASE}/api/sdk/trade",
                     headers=headers,
                     json=payload,
                     timeout=5)
    
    print(f"\nResponse Status: {r.status_code}")
    print(f"Full Response:")
    print(json.dumps(r.json(), indent=2))
else:
    print("No market found")
