#!/usr/bin/env python3
"""Execute real trades - CORRECT payload format."""

import requests
import json
from datetime import datetime, timezone

NEW_KEY = "sk_live_484943fcabd5d3dd5e58106872e6831aedbd340139736760dc10773c47471570"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {NEW_KEY}"}

print("\n" + "="*80)
print("FINAL EXECUTION - Correct Payload")
print("="*80)

try:
    # Get portfolio
    r = requests.get(f"{SIMMER_BASE}/api/sdk/portfolio", 
                    headers=headers, timeout=3)
    balance = float(r.json().get('balance_usdc', 0))
    
    print(f"\n[BALANCE] ${balance:.2f}")
    
    # Get markets
    r = requests.get(f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=500", 
                    headers=headers, timeout=5)
    markets = r.json().get('markets', [])
    
    now = datetime.now(timezone.utc)
    crypto_markets = []
    
    for m in markets:
        q = m.get('question', '').lower()
        
        if any(x in q for x in ['bitcoin', 'btc', 'ethereum', 'eth', 'solana', 'sol']):
            current_price = m.get('current_price')
            
            if current_price and current_price > 0:
                try:
                    expires_str = m.get('resolves_at', '')
                    expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
                    seconds = (expires_at - now).total_seconds()
                    
                    if seconds > 0:
                        crypto_markets.append({
                            'id': m['id'],
                            'question': m.get('question'),
                            'price': float(current_price),
                            'expires': int(seconds),
                        })
                except:
                    pass
    
    crypto_markets.sort(key=lambda x: x['expires'])
    
    print(f"[CRYPTO MARKETS] {len(crypto_markets)} with valid prices")
    
    if not crypto_markets:
        print("No markets found!")
    else:
        print("\nTop 3 (nearest expiry):\n")
        for i, m in enumerate(crypto_markets[:3], 1):
            symbol = "BTC" if "btc" in m['question'].lower() else "ETH" if "eth" in m['question'].lower() else "SOL"
            print(f"{i}. [{symbol}] {m['question'][:50]}")
            print(f"   Expires: {m['expires']/3600:.2f}h | Price: ${m['price']:.4f}")
        
        # CONSERVATIVE STRATEGY: Diversified small bets
        print("\n" + "="*80)
        print("DEPLOYING: $1.50 x 3 bets (conservative diversification)")
        print("="*80)
        
        executed = []
        bets_made = 0
        
        for i, market in enumerate(crypto_markets[:3], 1):
            if balance < 1.50:
                print(f"\nBet {i}: Insufficient balance (${balance:.2f})")
                break
            
            print(f"\n[Bet {i}]")
            print(f"Market: {market['question'][:50]}")
            
            # Simple bias: BTC/ETH UP in bull market, SOL is risky
            if 'solana' in market['question'].lower():
                side = "no"  # Bet SOL DOWN (more conservative)
            else:
                side = "yes"  # BTC/ETH UP
            
            print(f"Bet: $1.50 on {side.upper()}")
            
            # CORRECT PAYLOAD
            payload = {
                "market_id": market['id'],
                "side": side,
                "amount": 1.50,  # NOT amount_usd
            }
            
            try:
                r = requests.post(f"{SIMMER_BASE}/api/sdk/trade",
                                 headers=headers,
                                 json=payload,
                                 timeout=5)
                
                response = r.json()
                
                if response.get('success') == True:
                    trade_id = response.get('trade_id')
                    cost = response.get('cost', 1.50)
                    
                    executed.append({
                        'market': market['question'],
                        'side': side,
                        'amount': 1.50,
                        'trade_id': trade_id,
                    })
                    
                    balance -= cost
                    bets_made += 1
                    
                    print(f"✓ EXECUTED | Trade ID: {trade_id}")
                    print(f"  Cost: ${cost:.2f} | Balance left: ${balance:.2f}")
                else:
                    error = response.get('error', 'unknown')
                    print(f"✗ FAILED | {error}")
            
            except Exception as e:
                print(f"✗ ERROR | {str(e)[:80]}")
        
        # Summary
        if executed:
            print("\n" + "="*80)
            print("EXECUTED SUCCESSFULLY")
            print("="*80)
            print(f"\nTrades placed: {len(executed)}")
            print(f"Capital deployed: ${sum(t['amount'] for t in executed):.2f}")
            print(f"Balance remaining: ${balance:.2f}")
            
            print("\nPositions:")
            for t in executed:
                print(f"  • {t['market'][:45]} | ${t['amount']:.2f} on {t['side'].upper()}")
            
            print(f"\nWin scenario: If all hit, return ~${sum(t['amount'] * 2 for t in executed):.2f}")
            print(f"Profit potential: ~${sum(t['amount'] for t in executed):.2f}")
            
            # Save
            with open('active_trades.json', 'w') as f:
                json.dump(executed, f, indent=2)
            
            print("\n[Trades saved to active_trades.json]")
        else:
            print("\nNo trades executed")

except Exception as e:
    print(f"\n[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()

print("\n")
