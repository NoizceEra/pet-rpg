#!/usr/bin/env python3
"""Find markets with obvious or likely outcomes we can exploit."""

import requests
from datetime import datetime, timezone

SIMMER_API_KEY = "sk_live_8b62db698791339edac7246d599ee05671f5ad36a0e2b1e2b53e3ceaf7db0cc6"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}

print("\n" + "="*80)
print("LIKELY OUTCOME HUNT - Markets we can exploit")
print("="*80)

try:
    r = requests.get(f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=500", 
                    headers=headers, timeout=5)
    markets = r.json().get('markets', [])
    
    now = datetime.now(timezone.utc)
    
    # Categorize by likelihood patterns
    obvious_wins = []
    short_term = []
    volatility_plays = []
    
    for m in markets:
        q = m.get('question', '').lower()
        
        try:
            expires_str = m.get('resolves_at', '')
            expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
            seconds = (expires_at - now).total_seconds()
            
            if seconds < 600 or seconds > 21600:
                continue
            
            yes_price = float(m.get('yes_price', 0.5))
            no_price = float(m.get('no_price', 0.5))
            
            # Pattern 1: Over/Under markets (usually settled by data)
            if 'over' in q or 'under' in q or 'o/u' in q:
                volatility_plays.append({
                    'q': m.get('question'),
                    'yes': yes_price,
                    'no': no_price,
                    'exp': int(seconds),
                    'reason': 'O/U markets often have clear outcomes',
                })
            
            # Pattern 2: Very short-term (next 10-30 min)
            if seconds < 1800:
                short_term.append({
                    'q': m.get('question'),
                    'yes': yes_price,
                    'no': no_price,
                    'exp': int(seconds),
                    'reason': 'Quick resolution (~' + f"{seconds/60:.0f}" + 'min)',
                })
            
            # Pattern 3: Obvious outcomes (e.g., team with much better record)
            # Hard to detect without external data, so flag anything with question hints
            if any(x in q for x in ['favorite', 'favorite team', 'strong', 'likely']):
                obvious_wins.append({
                    'q': m.get('question'),
                    'yes': yes_price,
                    'no': no_price,
                    'exp': int(seconds),
                    'reason': 'Language suggests likely outcome',
                })
        
        except:
            pass
    
    print("\n[SHORT-TERM MARKETS] (Next 30 min - highest resolution risk/reward)")
    if short_term:
        short_term.sort(key=lambda x: x['exp'])
        for i, m in enumerate(short_term[:5], 1):
            print(f"{i}. {m['q'][:65]}")
            print(f"   Expires: {m['exp']/60:.1f} min")
            print(f"   YES: ${m['yes']:.3f} | NO: ${m['no']:.3f}")
            print(f"   Strategy: Bet whichever side seems likely, quick $$ if right")
            print()
    
    print("\n[OVER/UNDER MARKETS] (Data-driven)")
    if volatility_plays:
        volatility_plays.sort(key=lambda x: x['exp'])
        for i, m in enumerate(volatility_plays[:5], 1):
            print(f"{i}. {m['q'][:65]}")
            print(f"   Expires: {m['exp']/60:.1f} min")
            print(f"   Strategy: Research the stat, bet data-driven outcome")
            print()
    
    print("\n[STRATEGY FOR $7.96]")
    print("="*80)
    print("\nWith only $7.96, you need RISKY but likely wins:")
    print("\nOption 1: Multi-bet strategy")
    print("  Split $7.96 across 3-4 short-expiry markets")
    print("  If 2 hit: $2.65/2 = $1.33 profit per win")
    print("  If all 4 hit: $7.96 * (1/0.5) = potential 2x = $15.92")
    print("\nOption 2: Go-all-in on ONE high-confidence market")
    print("  Bet all $7.96 on one likely outcome")
    print("  Win = ~$16 (2x return)")
    print("  Lose = $0 (risky but need fast $)")
    print("\nOption 3: Find/research market using external data")
    print("  Use real-world info (sports scores, crypto prices) to identify")
    print("  markets where outcome is >55% likely")
    print("  Then bet YES/NO accordingly")
    
except Exception as e:
    print("[ERROR] " + str(e))

print("\n")
