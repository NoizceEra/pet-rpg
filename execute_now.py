#!/usr/bin/env python3
"""Execute the trades now."""

import requests
import json

SIMMER_API_KEY = "sk_live_8b62db698791339edac7246d599ee05671f5ad36a0e2b1e2b53e3ceaf7db0cc6"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}

# Load plays
with open('plays_to_execute.json', 'r') as f:
    plays = json.load(f)

print("\n" + "="*80)
print("EXECUTING TRADES")
print("="*80)

executed = []

for i, play in enumerate(plays, 1):
    print(f"\n[{i}] {play['question'][:60]}")
    print(f"    Betting ${play['size']:.2f} on {play['side'].upper()}")
    
    try:
        payload = {
            "market_id": play['market_id'],
            "side": play['side'],
            "amount_usd": play['size'],
        }
        
        r = requests.post(f"{SIMMER_BASE}/api/sdk/trade",
                         headers=headers,
                         json=payload,
                         timeout=5)
        
        if r.status_code in [200, 201]:
            result = r.json()
            executed.append({
                'market': play['question'],
                'side': play['side'],
                'amount': play['size'],
                'entry_price': result.get('price', 0),
                'trade_id': result.get('id'),
            })
            
            print(f"    [OK] Entry: ${result.get('price', 0):.4f}")
            print(f"    Trade ID: {result.get('id')}")
        else:
            print(f"    [FAILED] Status: {r.status_code}")
            print(f"    {r.text[:100]}")
    
    except Exception as e:
        print(f"    [ERROR] {str(e)[:80]}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"\nExecuted: {len(executed)} trades")
print(f"Wagered: ${sum(p['amount'] for p in executed):.2f}")

if executed:
    print("\nTrades Placed:")
    for p in executed:
        print(f"  - {p['market'][:55]} | ${p['amount']:.2f} @ ${p['entry_price']:.4f}")
    
    print(f"\nIf ALL hit: Return ~${sum(p['amount'] * 2 for p in executed):.2f}")
    print(f"Profit potential: ~${sum(p['amount'] * 2 for p in executed) - sum(p['amount'] for p in executed):.2f}")
    
    # Auto-redeem reminder
    print("\n[AUTO-REDEEM] Wins will auto-redeem when positions resolve or you exit")
else:
    print("\nNo trades executed")

print("\n")
