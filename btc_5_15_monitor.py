#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Active monitor + executor for BTC 5-15min window."""

import requests
import json
from datetime import datetime, timezone
import time

NEW_KEY = "sk_live_484943fcabd5d3dd5e58106872e6831aedbd340139736760dc10773c47471570"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {NEW_KEY}"}

executed_markets = set()

print("\n" + "="*80)
print("BTC 5-15MIN ACTIVE MONITOR + EXECUTOR")
print("="*80)
print("\nScanning every 10 seconds for BTC markets in 5-15min window")
print("Will execute $1.00 on first suitable market found\n")

iteration = 0

while True:
    iteration += 1
    now = datetime.now(timezone.utc)
    time_str = now.strftime("%H:%M:%S")
    
    try:
        # Get all markets
        r = requests.get(f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=2000", 
                        headers=headers, timeout=10)
        markets = r.json().get('markets', [])
        
        # Find BTC in 5-15min window
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
        
        if candidates:
            candidates.sort(key=lambda x: x['mins'])
            
            # Report
            print(f"[{time_str}] FOUND {len(candidates)} BTC markets in 5-15min")
            for c in candidates[:3]:
                status = "[EXECUTED]" if c['id'] in executed_markets else "[READY]"
                print(f"  {status} {c['mins']}min | {c['question'][:45]} | ${c['price']:.4f}")
            
            # Try to execute on first not-yet-executed
            for market in candidates:
                if market['id'] not in executed_markets:
                    # Get balance first
                    r = requests.get(f"{SIMMER_BASE}/api/sdk/portfolio", 
                                    headers=headers, timeout=10)
                    balance = float(r.json().get('balance_usdc', 0))
                    
                    if balance >= 1.0:
                        print(f"\n  >>> EXECUTING on: {market['question'][:50]}")
                        print(f"      Bet: $1.00 on YES | Balance: ${balance:.2f}")
                        
                        payload = {
                            "market_id": market['id'],
                            "side": "yes",
                            "amount": 1.00,
                        }
                        
                        try:
                            r = requests.post(f"{SIMMER_BASE}/api/sdk/trade",
                                             headers=headers,
                                             json=payload,
                                             timeout=15)
                            
                            response = r.json()
                            
                            if response.get('success') == True:
                                trade_id = response.get('trade_id', '???')
                                cost = response.get('cost', 1.00)
                                
                                print(f"      SUCCESS | Trade ID: {trade_id}")
                                print(f"      Cost: ${cost:.2f}")
                                
                                executed_markets.add(market['id'])
                                
                                # Rate limit: wait 120s
                                print(f"      Waiting 120s for rate limit...")
                                time.sleep(120)
                            else:
                                error = response.get('error', 'unknown')
                                print(f"      FAILED: {error[:80]}")
                        
                        except Exception as e:
                            print(f"      ERROR: {str(e)[:80]}")
                        
                        print()
        else:
            print(f"[{time_str}] No BTC 5-15min markets (scan #{iteration})", end="\r")
        
        time.sleep(10)
    
    except Exception as e:
        print(f"[{time_str}] Error: {str(e)[:80]}")
        time.sleep(10)
