#!/usr/bin/env python3
"""Execute high-probability bets to generate $5-50 profit in 2-3 hours."""

import requests
import json
from datetime import datetime, timezone

SIMMER_API_KEY = "sk_live_8b62db698791339edac7246d599ee05671f5ad36a0e2b1e2b53e3ceaf7db0cc6"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}

print("\n" + "="*80)
print("EXECUTING PLAYS - TARGET: $5-50 PROFIT IN 2-3 HOURS")
print("="*80)

# Get markets
try:
    r = requests.get(f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=500", 
                    headers=headers, timeout=5)
    markets = r.json().get('markets', [])
    
    now = datetime.now(timezone.utc)
    
    # Target OU markets expiring 2-3 hours from now
    ou_markets = []
    
    for m in markets:
        q = m.get('question', '')
        
        try:
            expires_str = m.get('resolves_at', '')
            expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
            seconds = (expires_at - now).total_seconds()
            
            # 90min - 210min window
            if 5400 <= seconds <= 12600:
                if any(x in q.lower() for x in ['over', 'under', 'o/u']):
                    ou_markets.append({
                        'id': m['id'],
                        'question': q,
                        'yes_price': float(m.get('yes_price', 0.5)),
                        'no_price': float(m.get('no_price', 0.5)),
                        'exp_min': int(seconds / 60),
                    })
        except:
            pass
    
    ou_markets.sort(key=lambda x: x['exp_min'])
    
    print(f"\nFound {len(ou_markets)} O/U markets in 90-210min window")
    print("\nOPTIMAL BETS:")
    print("-" * 80)
    
    # Betting strategy for $7.96
    # PSG vs Monaco O/U 3.5 is high confidence (big team, home advantage = OVER likely)
    # Dota kills are high-volume games (usually high kill counts = OVER likely)
    
    plays = []
    
    for m in ou_markets:
        if "psg" in m['question'].lower() and "monaco" in m['question'].lower():
            plays.append({
                'market_id': m['id'],
                'question': m['question'],
                'side': 'yes',  # Over 3.5 goals likely for PSG at home
                'size': 4.00,
                'confidence': 'HIGH - PSG strong home team',
                'reason': 'O/U 3.5 - PSG at home, expected high-scoring match',
            })
        elif "kill" in m['question'].lower() and "game 2" in m['question'].lower():
            # Check if it's a high kill threshold
            if any(x in m['question'] for x in ['55', '57']):
                plays.append({
                    'market_id': m['id'],
                    'question': m['question'],
                    'side': 'yes',  # Over high kills likely in Dota 2
                    'size': 3.96,
                    'confidence': 'MEDIUM - Dota games usually have high kills',
                    'reason': 'Esports games tend toward high action/kills',
                })
    
    balance = requests.get(f"{SIMMER_BASE}/api/sdk/portfolio", 
                          headers=headers, timeout=3).json().get('balance_usdc', 0)
    
    total_bet = sum(p['size'] for p in plays)
    
    print(f"\nCurrent Balance: ${balance:.2f}")
    print(f"Planned Bets: {len(plays)}")
    print(f"Total to Wager: ${total_bet:.2f}")
    print()
    
    if total_bet > balance:
        print("[ADJUSTING] Total exceeds balance, scaling down...")
        plays = plays[:1]  # Just do the PSG play
        plays[0]['size'] = balance * 0.95
    
    # Display plays
    for i, play in enumerate(plays, 1):
        print(f"{i}. {play['question'][:60]}")
        print(f"   Bet: ${play['size']:.2f} on {play['side'].upper()}")
        print(f"   Confidence: {play['confidence']}")
        print(f"   Reason: {play['reason']}")
        print()
    
    # Execute?
    print("="*80)
    print("READY TO EXECUTE")
    print("="*80)
    print("\nIf all bets hit:")
    potential_return = sum(p['size'] * 2 for p in plays)
    print(f"  Total return: ${potential_return:.2f}")
    print(f"  Profit: ${potential_return - total_bet:.2f}")
    print("\nProceed? (saved for review)")
    
    # Save plays for execution
    with open('plays_to_execute.json', 'w') as f:
        json.dump(plays, f, indent=2)
    
    print("\nPlays saved to plays_to_execute.json")
    
except Exception as e:
    print("[ERROR] " + str(e))

print("\n")
