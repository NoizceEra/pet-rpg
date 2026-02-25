#!/usr/bin/env python3
"""List all markets to understand the landscape."""

import requests
import json
from datetime import datetime, timezone

SIMMER_API_KEY = "sk_live_8b62db698791339edac7246d599ee05671f5ad36a0e2b1e2b53e3ceaf7db0cc6"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}

print("\n[FETCHING ALL MARKETS]")

try:
    r = requests.get(f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=1000", 
                    headers=headers, timeout=5)
    markets = r.json().get('markets', [])
    
    print("Total active markets: " + str(len(markets)))
    
    # Check for any with imbalance
    now = datetime.now(timezone.utc)
    imbalanced = []
    
    for m in markets:
        yes_price = float(m.get('yes_price', 0.5))
        no_price = float(m.get('no_price', 0.5))
        imbalance = abs(yes_price - no_price)
        
        if imbalance > 0.001:
            try:
                expires_str = m.get('resolves_at', '')
                expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
                seconds = (expires_at - now).total_seconds()
                
                if seconds > 0:
                    imbalanced.append({
                        'q': m.get('question', ''),
                        'yes': yes_price,
                        'no': no_price,
                        'imb': imbalance,
                        'exp': int(seconds),
                    })
            except:
                pass
    
    if imbalanced:
        print("\nMarkets with ANY imbalance: " + str(len(imbalanced)))
        imbalanced.sort(key=lambda x: x['exp'])
        for m in imbalanced[:10]:
            print("  " + m['q'][:60] + " (Y:" + f"{m['yes']:.3f}" + " N:" + f"{m['no']:.3f}" + " E:" + f"{m['exp']/3600:.1f}" + "h)")
    else:
        print("\nNo imbalanced markets found - all perfectly 0.50/0.50")
    
    # Check markets by category
    print("\n[MARKET TYPES]")
    btc_count = len([m for m in markets if 'bitcoin' in m.get('question', '').lower() or 'btc' in m.get('question', '').lower()])
    eth_count = len([m for m in markets if 'ethereum' in m.get('question', '').lower() or 'eth' in m.get('question', '').lower()])
    sports_count = len([m for m in markets if any(x in m.get('question', '').lower() for x in ['nfl', 'nba', 'nhl', 'mlb', 'fc', 'vs', 'game'])])
    
    print("Crypto (BTC/ETH): " + str(btc_count + eth_count))
    print("Sports: " + str(sports_count))
    print("Other: " + str(len(markets) - btc_count - eth_count - sports_count))
    
except Exception as e:
    print("[ERROR] " + str(e))

print("\n")
