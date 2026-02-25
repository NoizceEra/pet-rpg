#!/usr/bin/env python3
"""Verify if trades actually exist on Simmer dashboard."""

import requests
import json

SIMMER_API_KEY = "sk_live_8b62db698791339edac7246d599ee05671f5ad36a0e2b1e2b53e3ceaf7db0cc6"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}

print("\n" + "="*80)
print("VERIFYING TRADE EXECUTION ON SIMMER")
print("="*80)

try:
    r = requests.get(f"{SIMMER_BASE}/api/sdk/portfolio", 
                    headers=headers, timeout=3)
    
    if r.status_code != 200:
        print(f"[ERROR] Portfolio fetch failed: {r.status_code}")
        print(r.text)
    else:
        portfolio = r.json()
        
        print("\n[PORTFOLIO STATUS]")
        balance = float(portfolio.get('balance_usdc', 0))
        print(f"USDC Balance: ${balance:.2f}")
        
        positions = portfolio.get('positions', [])
        print(f"Open Positions: {len(positions)}")
        
        if positions:
            print("\n[OPEN POSITIONS - DETAILED]")
            for pos in positions:
                print(f"\nMarket: {pos.get('market_name')}")
                print(f"  ID: {pos.get('id')}")
                print(f"  Side: {pos.get('side')}")
                print(f"  Amount: {pos.get('amount')}")
                print(f"  Entry Price: ${pos.get('entry_price', 0):.4f}")
                print(f"  Current Price: ${pos.get('current_price', 0):.4f}")
                print(f"  Current Value: ${pos.get('current_value', 0):.2f}")
                print(f"  Entry Cost: ${pos.get('entry_cost', 0):.2f}")
        else:
            print("\n[NO OPEN POSITIONS]")
            print("Trades did NOT execute or were not recorded by Simmer.")
        
        # Check trade history
        print("\n" + "="*80)
        print("[TRADE HISTORY CHECK]")
        
        try:
            history_r = requests.get(f"{SIMMER_BASE}/api/sdk/trades", 
                                    headers=headers, timeout=3)
            
            if history_r.status_code == 200:
                trades = history_r.json().get('trades', [])
                print(f"Total trades on record: {len(trades)}")
                
                if trades:
                    print("\nRecent trades:")
                    for t in trades[-3:]:
                        print(f"  - {t.get('market_name', '?')} | {t.get('side')} | ${t.get('amount', 0):.2f}")
            else:
                print(f"Trade history unavailable: {history_r.status_code}")
        except:
            print("Could not fetch trade history")
        
        print("\n" + "="*80)
        print("CONCLUSION")
        print("="*80)
        
        if len(positions) == 0 and balance == 7.96:
            print("\n[FALSE POSITIVES] API returned success but trades never executed.")
            print("Balance unchanged at $7.96 = trades were NOT placed.")
            print("\nWhy this happened:")
            print("- API may require additional params we're not sending")
            print("- Trade requests may be queued but not auto-executed")
            print("- API response parsing may be incorrect")
        elif balance < 7.96:
            print("\n[CONFIRMED] Trades executed and balance decreased.")
            print(f"Deployed: ${7.96 - balance:.2f}")
        else:
            print("\n[UNKNOWN STATE]")

except Exception as e:
    print(f"[ERROR] {str(e)}")

print("\n")
