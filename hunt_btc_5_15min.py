#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hunt BTC markets expiring in 5-15min window and execute trades."""

import requests
import json
from datetime import datetime, timezone
import time

NEW_KEY = "sk_live_484943fcabd5d3dd5e58106872e6831aedbd340139736760dc10773c47471570"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {NEW_KEY}"}

print("\n" + "="*80)
print("HUNTING BTC 5-15MIN MARKETS")
print("="*80)

def find_btc_5_15min(markets):
    """Find BTC markets expiring 5-15min from now."""
    now = datetime.now(timezone.utc)
    candidates = []
    
    for m in markets:
        q = m.get('question', '').lower()
        
        if 'bitcoin' not in q and 'btc' not in q:
            continue
        
        expires_str = m.get('resolves_at', '')
        try:
            expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
            secs = (expires_at - now).total_seconds()
            mins = secs / 60
            
            if 5 <= mins <= 15:
                candidates.append({
                    'question': m.get('question'),
                    'id': m['id'],
                    'price': m.get('current_price', 0),
                    'mins': int(mins),
                    'secs': int(secs),
                })
        except:
            pass
    
    return sorted(candidates, key=lambda x: x['mins'])

# Monitor loop
loop_count = 0
trades_executed = 0

while loop_count < 300:  # Run for 300 iterations (~15 min)
    loop_count += 1
    now_str = datetime.now(timezone.utc).strftime("%H:%M:%S")
    
    try:
        r = requests.get(f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=1000", 
                        headers=headers, timeout=10)
        markets = r.json().get('markets', [])
        
        candidates = find_btc_5_15min(markets)
        
        if candidates:
            # Get portfolio
            r = requests.get(f"{SIMMER_BASE}/api/sdk/portfolio", 
                            headers=headers, timeout=10)
            balance = float(r.json().get('balance_usdc', 0))
            
            print(f"\n[{now_str}] {len(candidates)} BTC markets in 5-15min window | Balance: ${balance:.2f}")
            
            for m in candidates[:3]:
                print(f"  {m['mins']}min | {m['question'][:50]} | ${m['price']:.4f}")
            
            # Execute on first suitable market
            if balance > 1.0 and candidates:
                market = candidates[0]
                
                # Simple logic: BTC price near 0.5 = uncertain, bet YES for upside
                side = "yes"
                amount = 1.00
                
                print(f"\n  >>> EXECUTING: ${amount:.2f} on {side.upper()}")
                
                payload = {
                    "market_id": market['id'],
                    "side": side,
                    "amount": amount,
                }
                
                try:
                    r = requests.post(f"{SIMMER_BASE}/api/sdk/trade",
                                     headers=headers,
                                     json=payload,
                                     timeout=15)
                    
                    response = r.json()
                    
                    if response.get('success') == True:
                        trade_id = response.get('trade_id')
                        cost = response.get('cost', amount)
                        
                        print(f"      [SUCCESS] Trade ID: {trade_id}")
                        print(f"      Cost: ${cost:.2f}")
                        
                        trades_executed += 1
                        
                        # Wait 120s before trading same market again (rate limit)
                        time.sleep(120)
                    else:
                        error = response.get('error', 'unknown')
                        print(f"      [FAILED] {error[:80]}")
                        time.sleep(10)
                
                except Exception as e:
                    print(f"      [ERROR] {str(e)[:80]}")
                    time.sleep(10)
        else:
            print(f"[{now_str}] No BTC 5-15min markets. Scanning... ({loop_count}/300)")
            time.sleep(3)
    
    except Exception as e:
        print(f"[{now_str}] Error: {str(e)[:80]}")
        time.sleep(5)

print(f"\n\nDONE | Executed {trades_executed} trades")
