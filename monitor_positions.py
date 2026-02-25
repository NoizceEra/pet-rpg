#!/usr/bin/env python3
"""Monitor active positions and auto-redeem winners."""

import requests
import json
import time
from datetime import datetime, timezone

SIMMER_API_KEY = "sk_live_8b62db698791339edac7246d599ee05671f5ad36a0e2b1e2b53e3ceaf7db0cc6"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}

print("\n" + "="*80)
print("MONITORING POSITIONS - Auto-Redeem on Wins")
print("="*80)

check_count = 0
max_checks = 360  # Check for 6 hours

while check_count < max_checks:
    check_count += 1
    now_time = datetime.now(timezone.utc).strftime("%H:%M:%S")
    
    try:
        # Get portfolio
        r = requests.get(f"{SIMMER_BASE}/api/sdk/portfolio", 
                        headers=headers, timeout=3)
        portfolio = r.json()
        
        balance = float(portfolio.get('balance_usdc', 0.0))
        positions = portfolio.get('positions', [])
        
        print(f"\n[{now_time}] Check #{check_count} | Balance: ${balance:.2f}")
        
        if not positions:
            print("  No open positions")
        
        else:
            print(f"  Open positions: {len(positions)}")
            
            for pos in positions:
                market = pos.get('market_name', '?')[:50]
                side = pos.get('side', '?')
                current_price = float(pos.get('current_price', 0.5))
                entry_price = float(pos.get('entry_price', 0.5))
                
                # Calculate P&L
                if entry_price > 0:
                    pnl_pct = ((current_price - entry_price) / entry_price) * 100
                else:
                    pnl_pct = 0
                
                pnl_amount = pos.get('current_value', 0) - pos.get('entry_cost', 0)
                
                status = "[GREEN]" if pnl_pct > 0 else "[RED]"
                
                print(f"  {status} {market}")
                print(f"      {side.upper()} @ ${entry_price:.4f} -> ${current_price:.4f} ({pnl_pct:+.1f}%)")
                
                # Auto-redeem if winning
                if current_price > entry_price and pnl_pct > 50:
                    print(f"      >> REDEEMING (winning position)")
                    try:
                        redeem_payload = {"trade_id": pos.get('id')}
                        rr = requests.post(f"{SIMMER_BASE}/api/sdk/redeem",
                                         headers=headers,
                                         json=redeem_payload,
                                         timeout=5)
                        if rr.status_code in [200, 201]:
                            print(f"      >> REDEEMED!")
                    except:
                        print(f"      >> Redeem failed, continuing...")
        
        # Break if balance changed significantly (trades resolved)
        if balance > 10:
            print(f"\n[SUCCESS] Balance now ${balance:.2f} - Positions resolved!")
            break
        
        # Wait 30 seconds before next check
        time.sleep(30)
    
    except Exception as e:
        print(f"  [ERROR] {str(e)[:60]}")
        time.sleep(30)

print("\n" + "="*80)
print("MONITORING COMPLETE")
print("="*80 + "\n")
