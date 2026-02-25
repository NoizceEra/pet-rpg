#!/usr/bin/env python3
"""Hunt for market imbalances we can exploit."""

import requests
from datetime import datetime, timezone

SIMMER_API_KEY = "sk_live_8b62db698791339edac7246d599ee05671f5ad36a0e2b1e2b53e3ceaf7db0cc6"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}

print("\n" + "="*80)
print("IMBALANCE HUNT - Find YES/NO spreads we can exploit")
print("="*80)

try:
    r = requests.get(f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=500", 
                    headers=headers, timeout=5)
    markets = r.json().get('markets', [])
    
    now = datetime.now(timezone.utc)
    candidates = []
    
    for m in markets:
        question = m.get('question', '')
        
        try:
            expires_str = m.get('resolves_at', '')
            expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
            seconds = (expires_at - now).total_seconds()
            
            # Target: Next 6 hours (can close faster)
            if 600 <= seconds <= 21600:
                yes_price = float(m.get('yes_price', 0.5))
                no_price = float(m.get('no_price', 0.5))
                
                # Look for imbalances
                imbalance = abs(yes_price - no_price)
                
                if imbalance > 0.05:  # More than 5% imbalance
                    total = yes_price + no_price
                    arb = 1.00 - total if total < 1.00 else 0
                    
                    candidates.append({
                        'id': m['id'],
                        'question': question,
                        'expires': int(seconds),
                        'yes': yes_price,
                        'no': no_price,
                        'imbalance': imbalance,
                        'arb_return': (arb / total * 100) if total < 1.00 else 0,
                    })
        except:
            pass
    
    # Sort by best arbitrage first
    candidates.sort(key=lambda x: x['arb_return'], reverse=True)
    
    print("\n[IMBALANCED MARKETS - 10min to 6hr expiry]")
    print("Total imbalanced: " + str(len(candidates)))
    
    if candidates:
        print("\nTop 15 (by arbitrage opportunity):\n")
        for i, m in enumerate(candidates[:15], 1):
            print(str(i) + ". " + m['question'][:70])
            print("   Expires: " + f"{m['expires']/60:.1f}" + "min")
            print("   YES: $" + f"{m['yes']:.3f}" + " | NO: $" + f"{m['no']:.3f}")
            print("   Imbalance: " + f"{m['imbalance']*100:.1f}%")
            
            if m['arb_return'] > 0:
                print("   [ARBITRAGE] Return: " + f"{m['arb_return']:.2f}%")
            else:
                # One-sided bet
                favored = "YES" if m['yes'] > m['no'] else "NO"
                odds = m['yes'] if favored == "YES" else m['no']
                print("   [ONESIDED] " + favored + " favored at $" + f"{odds:.3f}")
            print()
    
    # Also check for any YES+NO < 1.00
    arb_opportunities = [c for c in candidates if c['arb_return'] > 0]
    
    if arb_opportunities:
        print("\n" + "="*80)
        print("ARBITRAGE OPPORTUNITIES (YES + NO < $1.00)")
        print("="*80)
        for m in arb_opportunities[:5]:
            print("\n" + m['question'][:70])
            print("YES: $" + f"{m['yes']:.4f}" + " + NO: $" + f"{m['no']:.4f}" + " = $" + f"{m['yes']+m['no']:.4f}")
            print("Free profit: " + f"{m['arb_return']:.2f}%" + " per $1 bet")
            
            # Calculate how much we can make with $7.96
            profit = (1.00 - (m['yes'] + m['no'])) * 7.96
            print("With $7.96: +$" + f"{profit:.2f}")

except Exception as e:
    print("[ERROR] " + str(e))

print("\n")
