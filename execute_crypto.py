#!/usr/bin/env python3
"""Execute SOL Up/Down market - crypto-focused bet."""

import requests
import json
from datetime import datetime

SIMMER_API_KEY = "sk_live_8b62db698791339edac7246d599ee05671f5ad36a0e2b1e2b53e3ceaf7db0cc6"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}

print("\n" + "="*80)
print("CRYPTO BET - SOL Up/Down Market")
print("="*80)

# Get the SOL market
r = requests.get(f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=1000", 
                headers=headers, timeout=5)
markets = r.json().get('markets', [])

# Find SOL Up/Down 11 AM ET
sol_market = None
for m in markets:
    q = m.get('question', '')
    if 'solana' in q.lower() and 'up or down' in q.lower() and '11am' in q.lower():
        sol_market = m
        break

if not sol_market:
    # Try any SOL Up/Down
    for m in markets:
        q = m.get('question', '')
        if 'solana' in q.lower() and 'up or down' in q.lower():
            sol_market = m
            break

if sol_market:
    market_id = sol_market['id']
    question = sol_market.get('question')
    yes_price = float(sol_market.get('yes_price', 0.5))
    no_price = float(sol_market.get('no_price', 0.5))
    
    print(f"\nMarket: {question}")
    print(f"ID: {market_id}")
    print(f"YES (Up): ${yes_price:.3f} | NO (Down): ${no_price:.3f}")
    
    # Get balance
    r = requests.get(f"{SIMMER_BASE}/api/sdk/portfolio", headers=headers, timeout=3)
    balance = float(r.json().get('balance_usdc', 0.0))
    
    print(f"\nBalance: ${balance:.2f}")
    
    # Decision: BET ALL-IN on UP (SOL is strong in bull market)
    # Using all $7.96
    bet_size = balance * 0.95
    side = "yes"  # UP
    
    print(f"\nBET: ${bet_size:.2f} on {side.upper()} (SOL Up)")
    print("Thesis: Crypto in bull momentum, short-term window = higher edge")
    print(f"Win target: ~${bet_size * 2:.2f} return (+${bet_size:.2f} profit)")
    
    print("\nExecuting...")
    
    payload = {
        "market_id": market_id,
        "side": side,
        "amount_usd": bet_size,
    }
    
    try:
        r = requests.post(f"{SIMMER_BASE}/api/sdk/trade",
                         headers=headers,
                         json=payload,
                         timeout=5)
        
        if r.status_code in [200, 201]:
            result = r.json()
            print(f"\n[EXECUTED]")
            print(f"Trade ID: {result.get('id')}")
            print(f"Entry Price: ${result.get('price', 0.5):.4f}")
            print(f"Position: ${bet_size:.2f} on {side.upper()}")
            
            # Log it
            with open('crypto_trades.json', 'w') as f:
                json.dump({
                    'timestamp': str(datetime.now()),
                    'market': question,
                    'side': side,
                    'amount': bet_size,
                    'entry_price': result.get('price', 0.5),
                    'trade_id': result.get('id'),
                }, f, indent=2)
        
        else:
            print(f"\n[FAILED] Status: {r.status_code}")
            print(f"Response: {r.text[:200]}")
    
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")

else:
    print("[ERROR] Could not find SOL Up/Down market")

print("\n")
