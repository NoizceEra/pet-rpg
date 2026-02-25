#!/usr/bin/env python3
"""Explore Simmer API endpoints to find working price data."""

import requests
import json

NEW_KEY = "sk_live_484943fcabd5d3dd5e58106872e6831aedbd340139736760dc10773c47471570"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {NEW_KEY}"}

print("\n" + "="*80)
print("EXPLORING SIMMER ENDPOINTS")
print("="*80)

endpoints_to_test = [
    "/api/sdk/markets",
    "/api/sdk/markets?include_prices=true",
    "/api/sdk/markets?format=detailed",
    "/api/v1/markets",
    "/api/markets",
    "/api/sdk/live-prices",
    "/api/sdk/market-data",
]

for endpoint in endpoints_to_test:
    print(f"\n[{endpoint}]")
    try:
        r = requests.get(f"{SIMMER_BASE}{endpoint}", headers=headers, timeout=3)
        print(f"  Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            
            # Try to find a market with prices
            if isinstance(data, dict):
                markets = data.get('markets', [])
            elif isinstance(data, list):
                markets = data[:5]
            else:
                markets = []
            
            if markets:
                m = markets[0]
                print(f"  Sample: {m.get('question', m.get('name', str(m)[:40]))[:50]}")
                
                # Check for price fields
                price_fields = [k for k in m.keys() if 'price' in k.lower() or 'yes' in k.lower() or 'no' in k.lower()]
                if price_fields:
                    print(f"  Price fields: {price_fields}")
                    for field in price_fields[:3]:
                        val = m.get(field)
                        if val:
                            print(f"    {field}: {val}")
                else:
                    print(f"  No price/yes/no fields found")
                    print(f"  Available fields: {list(m.keys())[:8]}")
        else:
            print(f"  Error: {r.text[:80]}")
    
    except Exception as e:
        print(f"  Exception: {str(e)[:60]}")

print("\n" + "="*80)
print("OBSERVATION")
print("="*80)
print("\nIf no endpoint returns valid prices, the issue is likely:")
print("1. Simmer API requires authentication/setup in dashboard first")
print("2. Your account is not fully activated")
print("3. Prices are not live yet (markets may be in init phase)")
print("\nRecommendation: Check Simmer.Markets dashboard manually")
print("              - Verify account is active")
print("              - Check if API key has correct permissions")
print("              - See if prices appear in web UI")

print("\n")
