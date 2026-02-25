#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scan for BTC 5-15min markets right now."""

import requests
import json
from datetime import datetime, timezone

NEW_KEY = "sk_live_484943fcabd5d3dd5e58106872e6831aedbd340139736760dc10773c47471570"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {NEW_KEY}"}

print("\nSCAN: BTC 5-15MIN MARKETS\n")

try:
    r = requests.get(f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=1000", 
                    headers=headers, timeout=10)
    markets = r.json().get('markets', [])
    
    now = datetime.now(timezone.utc)
    
    # Find all BTC markets with timeframe breakdown
    btc_markets = []
    for m in markets:
        q = m.get('question', '').lower()
        
        if 'bitcoin' in q or 'btc' in q:
            expires_str = m.get('resolves_at', '')
            try:
                expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
                secs = (expires_at - now).total_seconds()
                mins = secs / 60
                
                if secs >= 0:
                    btc_markets.append({
                        'question': m.get('question'),
                        'id': m['id'],
                        'price': m.get('current_price', 0),
                        'mins': mins,
                    })
            except:
                pass
    
    print(f"Total BTC markets: {len(btc_markets)}\n")
    
    # Group by time window
    windows = {
        "0-5min": [],
        "5-10min": [],
        "10-15min": [],
        "15-30min": [],
        "30-60min": [],
        "1h+": [],
    }
    
    for m in btc_markets:
        mins = m['mins']
        if mins <= 5:
            windows["0-5min"].append(m)
        elif mins <= 10:
            windows["5-10min"].append(m)
        elif mins <= 15:
            windows["10-15min"].append(m)
        elif mins <= 30:
            windows["15-30min"].append(m)
        elif mins <= 60:
            windows["30-60min"].append(m)
        else:
            windows["1h+"].append(m)
    
    for window, markets_in_window in windows.items():
        count = len(markets_in_window)
        if count > 0:
            print(f"[{window}] {count} markets")
            for m in markets_in_window[:2]:
                print(f"  {m['question'][:55]} | {int(m['mins'])}min | ${m['price']:.4f}")
            if count > 2:
                print(f"  ... and {count - 2} more")
            print()
    
    # Focus on target window
    target = windows["5-10min"] + windows["10-15min"]
    
    if target:
        print("="*80)
        print("TARGET WINDOW (5-15min)")
        print("="*80)
        
        for m in sorted(target, key=lambda x: x['mins']):
            print(f"\n{int(m['mins'])}min | {m['question']}")
            print(f"  Price: ${m['price']:.4f}")
            print(f"  ID: {m['id']}")
    else:
        print("\n[NO MARKETS IN 5-15MIN WINDOW]")
        print("\nNext available:")
        soon = [m for m in btc_markets if m['mins'] <= 60]
        soon.sort(key=lambda x: x['mins'])
        for m in soon[:5]:
            print(f"  {int(m['mins'])}min | {m['question'][:50]}")

except Exception as e:
    print(f"Error: {str(e)}")

print("\n")
