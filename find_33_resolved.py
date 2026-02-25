#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find '33 resolved' market and 5-15min resolution markets on Simmer."""

import requests
import json
from datetime import datetime, timezone

NEW_KEY = "sk_live_484943fcabd5d3dd5e58106872e6831aedbd340139736760dc10773c47471570"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {NEW_KEY}"}

print("\n" + "="*80)
print("HUNTING FOR '33 RESOLVED' MARKET + 5-15MIN WINDOWS")
print("="*80)

try:
    r = requests.get(f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=1000", 
                    headers=headers, timeout=10)
    markets = r.json().get('markets', [])
    
    now = datetime.now(timezone.utc)
    
    # Look for "33 resolved"
    print("\n[SEARCHING FOR '33 RESOLVED']")
    
    matches = []
    for m in markets:
        q = m.get('question', '').lower()
        if '33' in q and 'resolv' in q:
            matches.append(m)
        elif 'resolved' in q and '33' in q:
            matches.append(m)
    
    if matches:
        print(f"Found {len(matches)} matches:")
        for m in matches:
            print(f"  - {m.get('question')}")
            print(f"    ID: {m['id']}")
            expires_str = m.get('resolves_at', '')
            expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
            secs = (expires_at - now).total_seconds()
            mins = int(secs / 60)
            print(f"    Expires in: {mins} min(s)")
    else:
        print("No exact matches. Searching broadly...")
        
        # List first 20 markets
        print("\nAll active markets (showing first 20):\n")
        for i, m in enumerate(markets[:20], 1):
            q = m.get('question', '')
            expires_str = m.get('resolves_at', '')
            expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
            secs = (expires_at - now).total_seconds()
            mins = int(secs / 60)
            
            print(f"{i}. {q[:60]}")
            print(f"   Expires: {mins}min | Price: ${m.get('current_price', 0):.4f}")
    
    # Find 5-15 min windows
    print("\n" + "="*80)
    print("[MARKETS WITH 5-15 MIN RESOLUTION]")
    print("="*80)
    
    quick_markets = []
    for m in markets:
        expires_str = m.get('resolves_at', '')
        try:
            expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
            secs = (expires_at - now).total_seconds()
            mins = secs / 60
            
            if 5 <= mins <= 15:
                quick_markets.append({
                    'question': m.get('question'),
                    'id': m['id'],
                    'price': m.get('current_price', 0),
                    'expires_min': int(mins),
                })
        except:
            pass
    
    if quick_markets:
        print(f"\nFound {len(quick_markets)} markets in 5-15min window:\n")
        for m in quick_markets:
            print(f"  {m['question'][:60]}")
            print(f"    {m['expires_min']}min | Price: ${m['price']:.4f}")
            print(f"    ID: {m['id']}\n")
    else:
        print("\nNo 5-15min markets found. Checking broader ranges...")
        
        ranges = {
            "1-5min": [],
            "5-10min": [],
            "10-15min": [],
            "15-30min": [],
        }
        
        for m in markets:
            expires_str = m.get('resolves_at', '')
            try:
                expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
                secs = (expires_at - now).total_seconds()
                mins = secs / 60
                
                if mins < 0:
                    continue
                
                if mins <= 5:
                    ranges["1-5min"].append(m)
                elif mins <= 10:
                    ranges["5-10min"].append(m)
                elif mins <= 15:
                    ranges["10-15min"].append(m)
                elif mins <= 30:
                    ranges["15-30min"].append(m)
            except:
                pass
        
        for range_name, range_markets in ranges.items():
            print(f"\n{range_name}: {len(range_markets)} markets")
            if range_markets:
                for m in range_markets[:3]:
                    print(f"  - {m.get('question')[:50]}")

except Exception as e:
    print(f"\n[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()

print("\n")
