#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monitor live positions for wins/losses."""

import requests
import json
from datetime import datetime, timezone
import time

NEW_KEY = "sk_live_484943fcabd5d3dd5e58106872e6831aedbd340139736760dc10773c47471570"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {NEW_KEY}"}

print("\nMONITORING LIVE POSITIONS\n")

check_num = 0
while check_num < 1440:  # Monitor for 24 hours
    check_num += 1
    now = datetime.now(timezone.utc).strftime("%H:%M:%S")
    
    try:
        r = requests.get(f"{SIMMER_BASE}/api/sdk/portfolio", 
                        headers=headers, timeout=10)
        portfolio = r.json()
        
        balance = float(portfolio.get('balance_usdc', 0))
        positions = portfolio.get('positions', [])
        
        status = "[" + now + "] Check #" + str(check_num) + " | Balance: $" + f"{balance:.2f}"
        
        if len(positions) == 0:
            # All positions closed
            if balance > 5.00:
                print(status + " | PROFIT DETECTED")
                print("Positions closed. Balance increased. WIN!")
                break
            elif balance < 4.00:
                print(status + " | LOSS DETECTED")
                print("Positions closed. Balance decreased. LOSS.")
                break
            else:
                print(status + " | Positions resolved (checking...)")
        else:
            print(status + " | Positions open: " + str(len(positions)))
            
            for pos in positions:
                market = pos.get('market_name', '?')[:35]
                current_price = pos.get('current_price', 0)
                entry_price = pos.get('entry_price', 0)
                
                if entry_price > 0:
                    pnl = ((current_price - entry_price) / entry_price) * 100
                    print("    " + market + " | " + f"{current_price:.4f}" + " (" + f"{pnl:+.1f}%" + ")")
        
        # Check every 30 seconds
        time.sleep(30)
    
    except Exception as e:
        print("[" + now + "] Error: " + str(e)[:60])
        time.sleep(30)

print("\nMONITORING COMPLETE")
