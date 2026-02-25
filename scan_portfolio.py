#!/usr/bin/env python3
"""Scan full Simmer portfolio for profitable opportunities."""

import requests
import json
from datetime import datetime, timezone

SIMMER_API_KEY = "sk_live_8b62db698791339edac7246d599ee05671f5ad36a0e2b1e2b53e3ceaf7db0cc6"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}

print("\n" + "="*80)
print("SIMMER PORTFOLIO SCAN - OPPORTUNITY HUNT")
print("="*80)

# Get portfolio
try:
    r = requests.get(f"{SIMMER_BASE}/api/sdk/portfolio", headers=headers, timeout=3)
    portfolio = r.json()
    
    print("\n[PORTFOLIO]")
    print("USDC Balance: $" + f"{portfolio.get('balance_usdc', 0):.2f}")
    print("Total Value: $" + f"{portfolio.get('portfolio_value', 0):.2f}")
    
    # Get positions
    positions = portfolio.get('positions', [])
    if positions:
        print("\n[OPEN POSITIONS]")
        for pos in positions:
            print("  Market: " + pos.get('market_name', '?')[:50])
            print("    Side: " + pos.get('side', '?'))
            print("    Amount: " + str(pos.get('amount', 0)))
            print("    Current Value: $" + f"{pos.get('current_value', 0):.2f}")
            print("    Entry: $" + f"{pos.get('entry_price', 0):.4f}")
            print("    Current: $" + f"{pos.get('current_price', 0):.4f}")
            pnl_pct = ((pos.get('current_price', 0) - pos.get('entry_price', 0)) / pos.get('entry_price', 1)) * 100 if pos.get('entry_price') else 0
            print("    P&L: " + f"{pnl_pct:+.2f}%")
            print()
    else:
        print("\n[OPEN POSITIONS] None")
    
except Exception as e:
    print("[ERROR] Portfolio: " + str(e))

# Get all active markets sorted by expiry
try:
    r = requests.get(f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=200", 
                    headers=headers, timeout=5)
    markets = r.json().get('markets', [])
    
    now = datetime.now(timezone.utc)
    
    # Find high-volatility, short-expiry markets
    hot_markets = []
    
    for m in markets:
        question = m.get('question', '')
        
        try:
            expires_str = m.get('resolves_at', '')
            expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
            seconds = (expires_at - now).total_seconds()
            
            # Focus on 30min-3hour window
            if 1800 <= seconds <= 10800:
                yes_price = float(m.get('yes_price', 0.5))
                no_price = float(m.get('no_price', 0.5))
                spread = abs(yes_price - no_price)
                
                hot_markets.append({
                    'id': m['id'],
                    'question': question,
                    'expires_in': int(seconds),
                    'yes': yes_price,
                    'no': no_price,
                    'spread': spread,
                })
        except:
            pass
    
    # Sort by earliest expiry first
    hot_markets.sort(key=lambda x: x['expires_in'])
    
    print("\n[HOT MARKETS - 30min to 3hr expiry]")
    print("Total: " + str(len(hot_markets)))
    
    if hot_markets:
        print("\nTop 10 (by earliest expiry):\n")
        for i, m in enumerate(hot_markets[:10], 1):
            print(str(i) + ". " + m['question'][:70])
            print("   Expires: " + str(m['expires_in']) + "s (" + f"{m['expires_in']/60:.1f}" + "min)")
            print("   YES: $" + f"{m['yes']:.4f} | NO: $" + f"{m['no']:.4f} | Spread: " + f"{m['spread']:.4f}")
            
            # Find arbitrage (if yes+no < 1.00)
            total = m['yes'] + m['no']
            if total < 1.00:
                arb_return = ((1.00 - total) / total) * 100
                print("   [ARBITRAGE] YES+NO=$" + f"{total:.4f}" + " -> " + f"{arb_return:.2f}%" + " return")
            print()
    else:
        print("None found")

except Exception as e:
    print("[ERROR] Markets: " + str(e))

print("\n" + "="*80)
print("STRATEGY: Find tight spreads or arbitrage in 30min-3hr window")
print("Target: $5-50 profit in next 2-3 hours")
print("="*80 + "\n")
