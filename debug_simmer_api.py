#!/usr/bin/env python3
"""Debug Simmer API responses in detail."""

import requests
import json

SIMMER_API_KEY = "sk_live_8b62db698791339edac7246d599ee05671f5ad36a0e2b1e2b53e3ceaf7db0cc6"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}

print("\n" + "="*80)
print("DEBUGGING SIMMER API")
print("="*80)

# Test 1: Portfolio endpoint
print("\n[TEST 1] Portfolio Endpoint")
try:
    r = requests.get(f"{SIMMER_BASE}/api/sdk/portfolio", 
                    headers=headers, timeout=3)
    print(f"Status: {r.status_code}")
    print(f"Response type: {type(r.json())}")
    print(f"Keys: {list(r.json().keys())}")
    print(f"Full response:\n{json.dumps(r.json(), indent=2)[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Get one market
print("\n[TEST 2] Get Single Market")
try:
    r = requests.get(f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=1", 
                    headers=headers, timeout=3)
    market = r.json().get('markets', [{}])[0]
    print(f"Market: {market.get('question')[:60]}")
    print(f"Market ID: {market.get('id')}")
    print(f"YES price: {market.get('yes_price')}")
    print(f"NO price: {market.get('no_price')}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Try trade with different payload formats
print("\n[TEST 3] Trade Execution - Format A (current)")
try:
    market_id = market.get('id')
    payload_a = {
        "market_id": market_id,
        "side": "yes",
        "amount_usd": 1.00,
    }
    r = requests.post(f"{SIMMER_BASE}/api/sdk/trade",
                     headers=headers,
                     json=payload_a,
                     timeout=5)
    print(f"Status: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2)[:300]}")
except Exception as e:
    print(f"Error: {e}")

# Test 4: Try alternative endpoint
print("\n[TEST 4] Try Alternative Trade Endpoint")
try:
    payload_b = {
        "market_id": market_id,
        "side": "yes",
        "amount_usd": 1.00,
    }
    r = requests.post(f"{SIMMER_BASE}/api/v1/trades",
                     headers=headers,
                     json=payload_b,
                     timeout=5)
    print(f"Status: {r.status_code}")
    print(f"Response: {json.dumps(r.json() if r.status_code < 400 else {'error': r.text}, indent=2)[:300]}")
except Exception as e:
    print(f"Error: {e}")

# Test 5: Check available endpoints
print("\n[TEST 5] API Documentation")
print("Standard Simmer SDK endpoints:")
print("  GET  /api/sdk/portfolio")
print("  GET  /api/sdk/markets")
print("  POST /api/sdk/trade")
print("  POST /api/sdk/redeem")
print("  GET  /api/sdk/trades")
print("\nIf trade endpoint requires different auth/format, check Simmer docs.")

print("\n")
