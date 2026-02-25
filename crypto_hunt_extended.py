#!/usr/bin/env python3
"""Hunt BTC, ETH, SOL markets - wider timeframe."""

import requests
import json
from datetime import datetime, timezone

SIMMER_API_KEY = "sk_live_8b62db698791339edac7246d599ee05671f5ad36a0e2b1e2b53e3ceaf7db0cc6"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}

print("\n" + "="*80)
print("CRYPTO HUNT - All BTC/ETH/SOL Markets (Any Timeframe)")
print("="*80)

try:
    r = requests.get(f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=1000", 
                    headers=headers, timeout=5)
    markets = r.json().get('markets', [])
    
    now = datetime.now(timezone.utc)
    
    crypto_markets = []
    
    for m in markets:
        q = m.get('question', '').lower()
        
        if any(x in q for x in ['bitcoin', 'btc', 'ethereum', 'eth', 'solana', 'sol']):
            try:
                expires_str = m.get('resolves_at', '')
                expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
                seconds = (expires_at - now).total_seconds()
                
                if seconds > 0:
                    yes_p = float(m.get('yes_price', 0.5))
                    no_p = float(m.get('no_price', 0.5))
                    
                    crypto_markets.append({
                        'question': m.get('question'),
                        'id': m['id'],
                        'yes': yes_p,
                        'no': no_p,
                        'expires_sec': int(seconds),
                        'expires_min': int(seconds / 60),
                        'expires_hr': round(seconds / 3600, 1),
                    })
            except:
                pass
    
    # Sort by closest expiry
    crypto_markets.sort(key=lambda x: x['expires_sec'])
    
    print(f"\nTotal BTC/ETH/SOL markets: {len(crypto_markets)}")
    
    if crypto_markets:
        print("\nAll crypto markets (by expiry):\n")
        for i, m in enumerate(crypto_markets[:20], 1):
            symbol = "BTC" if "btc" in m['question'].lower() else "ETH" if "eth" in m['question'].lower() else "SOL"
            
            print(f"{i}. [{symbol}] {m['question'][:60]}")
            if m['expires_min'] < 60:
                print(f"   EXPIRES: {m['expires_min']}min | YES: ${m['yes']:.3f} | NO: ${m['no']:.3f}")
            else:
                print(f"   EXPIRES: {m['expires_hr']}h | YES: ${m['yes']:.3f} | NO: ${m['no']:.3f}")
            print()
        
        # Find ones expiring soon
        soon = [m for m in crypto_markets if m['expires_min'] <= 240]
        if soon:
            print("\n" + "="*80)
            print(f"NEAR-TERM: {len(soon)} markets expiring in next 4 hours")
            print("="*80)
            for m in soon[:10]:
                symbol = "BTC" if "btc" in m['question'].lower() else "ETH" if "eth" in m['question'].lower() else "SOL"
                print(f"\n[{symbol}] {m['question'][:70]}")
                print(f"    Expires: {m['expires_min']}min")
                print(f"    YES: ${m['yes']:.3f} | NO: ${m['no']:.3f}")
    else:
        print("\nNo crypto markets found!")
    
    print("\n" + "="*80)
    print("STRATEGY: Focus on 1-4 hour window for $7.96 deployment")
    print("="*80)

except Exception as e:
    print("[ERROR] " + str(e))
    import traceback
    traceback.print_exc()

print("\n")
