#!/usr/bin/env python3
"""Test new Simmer API key."""

import requests
import json

NEW_KEY = "sk_live_484943fcabd5d3dd5e58106872e6831aedbd340139736760dc10773c47471570"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {NEW_KEY}"}

print("\n" + "="*80)
print("TESTING NEW API KEY")
print("="*80)

# Test 1: Portfolio
print("\n[Portfolio]")
try:
    r = requests.get(f"{SIMMER_BASE}/api/sdk/portfolio", 
                    headers=headers, timeout=3)
    if r.status_code == 200:
        portfolio = r.json()
        balance = portfolio.get('balance_usdc', 0)
        print(f"Status: 200 OK")
        print(f"Balance: ${balance:.2f}")
    else:
        print(f"Status: {r.status_code}")
        print(f"Error: {r.text[:100]}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Markets with prices
print("\n[Markets - Check for Valid Prices]")
try:
    r = requests.get(f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=50", 
                    headers=headers, timeout=5)
    
    if r.status_code == 200:
        markets = r.json().get('markets', [])
        print(f"Total markets: {len(markets)}")
        
        # Find one with prices
        with_prices = []
        for m in markets[:20]:
            yes_p = m.get('yes_price')
            no_p = m.get('no_price')
            
            if yes_p and no_p and yes_p > 0 and no_p > 0:
                with_prices.append({
                    'q': m.get('question'),
                    'yes': yes_p,
                    'no': no_p,
                    'id': m['id'],
                })
        
        print(f"Markets with valid prices: {len(with_prices)}")
        
        if with_prices:
            print("\nSample markets:")
            for m in with_prices[:3]:
                print(f"  {m['q'][:55]}")
                print(f"    YES: ${m['yes']:.4f} | NO: ${m['no']:.4f}")
                print(f"    ID: {m['id']}")
        else:
            print("No markets have valid prices (same issue as old key)")
    else:
        print(f"Status: {r.status_code}")

except Exception as e:
    print(f"Error: {e}")

# Test 3: Try small trade
if with_prices and balance > 1:
    print("\n[Test Trade - $1.00]")
    market = with_prices[0]
    
    payload = {
        "market_id": market['id'],
        "side": "yes",
        "amount_usd": 1.00,
    }
    
    try:
        r = requests.post(f"{SIMMER_BASE}/api/sdk/trade",
                         headers=headers,
                         json=payload,
                         timeout=5)
        
        response = r.json()
        
        print(f"Status: {r.status_code}")
        print(f"Success: {response.get('success')}")
        
        if response.get('success'):
            print(f"Trade ID: {response.get('trade_id')}")
            print(f"Cost: ${response.get('cost', 0):.2f}")
            print(f"New Price: ${response.get('new_price', 0):.4f}")
        else:
            print(f"Response: {json.dumps(response, indent=2)[:300]}")
    
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "="*80)
