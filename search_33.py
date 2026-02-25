#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deep search for '33 resolved' and any variation."""

import requests
import json
from datetime import datetime, timezone

NEW_KEY = "sk_live_484943fcabd5d3dd5e58106872e6831aedbd340139736760dc10773c47471570"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {NEW_KEY}"}

print("\nSEARCHING ALL MARKETS FOR '33 RESOLVED'\n")

try:
    r = requests.get(f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=2000", 
                    headers=headers, timeout=10)
    markets = r.json().get('markets', [])
    
    print(f"Total active markets: {len(markets)}\n")
    
    # Search variations
    searches = [
        ("'33 resolved'", lambda q: '33' in q.lower() and 'resolv' in q.lower()),
        ("'33'", lambda q: '33' in q.lower()),
        ("'resolved'", lambda q: 'resolv' in q.lower()),
    ]
    
    for search_name, search_fn in searches:
        matches = [m for m in markets if search_fn(m.get('question', '').lower())]
        print(f"[{search_name}] {len(matches)} matches")
        
        if matches:
            for m in matches[:5]:
                print(f"  - {m.get('question')}")
    
    # Also show any market with numeric ID patterns
    print("\n[MARKETS WITH SHORT EXPIRY - Full List]")
    
    now = datetime.now(timezone.utc)
    short_expiry = []
    
    for m in markets:
        try:
            expires_str = m.get('resolves_at', '')
            expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
            secs = (expires_at - now).total_seconds()
            
            if 0 <= secs <= 900:  # 0-15 minutes
                short_expiry.append({
                    'q': m.get('question'),
                    'id': m['id'],
                    'mins': int(secs / 60),
                    'price': m.get('current_price', 0),
                })
        except:
            pass
    
    short_expiry.sort(key=lambda x: x['mins'])
    
    if short_expiry:
        print(f"\nFound {len(short_expiry)} markets expiring in next 15min:\n")
        for m in short_expiry:
            print(f"{m['mins']}min | {m['q'][:55]}")
            print(f"     Price: ${m['price']:.4f} | ID: {m['id']}\n")
    else:
        print("No markets in 0-15min window")
    
    # Show ALL markets with question containing numbers
    print("\n[SAMPLE: Markets with Numbers in Question]")
    numeric = [m for m in markets if any(c.isdigit() for c in m.get('question', ''))][:10]
    for m in numeric:
        print(f"  - {m.get('question')}")

except Exception as e:
    print(f"Error: {str(e)}")

print("\n")
