#!/usr/bin/env python3
"""Real crypto execution - FIXED API checks."""

import requests
import json
from datetime import datetime, timezone

SIMMER_API_KEY = "sk_live_8b62db698791339edac7246d599ee05671f5ad36a0e2b1e2b53e3ceaf7db0cc6"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}

print("\n" + "="*80)
print("REAL EXECUTION - Conservative Small Bites Strategy")
print("="*80)

# Find markets with VALID prices
try:
    r = requests.get(f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=500", 
                    headers=headers, timeout=5)
    markets = r.json().get('markets', [])
    
    now = datetime.now(timezone.utc)
    
    valid_crypto = []
    
    for m in markets:
        q = m.get('question', '').lower()
        
        if any(x in q for x in ['bitcoin', 'btc', 'ethereum', 'eth', 'solana', 'sol']):
            yes_p = m.get('yes_price')
            no_p = m.get('no_price')
            
            # MUST have prices
            if yes_p and no_p and yes_p > 0 and no_p > 0:
                try:
                    expires_str = m.get('resolves_at', '')
                    expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
                    seconds = (expires_at - now).total_seconds()
                    
                    if seconds > 0:
                        valid_crypto.append({
                            'id': m['id'],
                            'question': m.get('question'),
                            'yes': float(yes_p),
                            'no': float(no_p),
                            'expires': int(seconds),
                        })
                except:
                    pass
    
    valid_crypto.sort(key=lambda x: x['expires'])
    
    print(f"\nValid crypto markets (with prices): {len(valid_crypto)}")
    
    if not valid_crypto:
        print("[NO VALID MARKETS] - All prices are null/zero")
    else:
        print("\nNear-term markets:\n")
        for m in valid_crypto[:10]:
            symbol = "BTC" if "btc" in m['question'].lower() else "ETH" if "eth" in m['question'].lower() else "SOL"
            print(f"{symbol} | {m['question'][:60]}")
            print(f"     YES: ${m['yes']:.3f} | NO: ${m['no']:.3f} | {m['expires']/3600:.1f}h")
        
        # Get balance
        r = requests.get(f"{SIMMER_BASE}/api/sdk/portfolio", headers=headers, timeout=3)
        balance = float(r.json().get('balance_usdc', 0.0))
        
        print(f"\n[CAPITAL: ${balance:.2f}]")
        print("\nConservative Strategy: Small diversified bets")
        print("  Bet 1: $1.50 on nearest-term market")
        print("  Bet 2: $1.50 on 2nd nearest-term")
        print("  Bet 3: $1.50 on 3rd market")
        print("  Reserve: $3.46 for next cycle")
        print("\nSmall bites, test execution, scale if working.")
        
        # Try Bet 1
        if valid_crypto and balance >= 1.50:
            market = valid_crypto[0]
            
            print(f"\n[EXECUTING BET 1]")
            print(f"Market: {market['question'][:60]}")
            print(f"Bet: $1.50 on YES (up bet)")
            
            payload = {
                "market_id": market['id'],
                "side": "yes",
                "amount_usd": 1.50,
            }
            
            r = requests.post(f"{SIMMER_BASE}/api/sdk/trade",
                             headers=headers,
                             json=payload,
                             timeout=5)
            
            response = r.json()
            
            # CHECK SUCCESS FIELD
            if response.get('success') == True:
                print(f"[OK] Trade executed")
                print(f"Trade ID: {response.get('trade_id')}")
                print(f"Cost: ${response.get('cost', 0):.2f}")
            else:
                print(f"[FAILED] API returned success=false")
                print(f"Error: {response}")

except Exception as e:
    print(f"[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()

print("\n")
