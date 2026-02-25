#!/usr/bin/env python3
"""Execute real crypto trades with correct API field names."""

import requests
import json
from datetime import datetime, timezone

NEW_KEY = "sk_live_484943fcabd5d3dd5e58106872e6831aedbd340139736760dc10773c47471570"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {NEW_KEY}"}

print("\n" + "="*80)
print("EXECUTING REAL CRYPTO TRADES - FIXED API")
print("="*80)

try:
    # Get portfolio
    r = requests.get(f"{SIMMER_BASE}/api/sdk/portfolio", 
                    headers=headers, timeout=3)
    balance = float(r.json().get('balance_usdc', 0))
    
    print(f"\n[BALANCE] ${balance:.2f}")
    
    if balance < 1.50:
        print("Insufficient balance for multi-bet strategy")
    
    # Get markets with CORRECT field names
    r = requests.get(f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=500", 
                    headers=headers, timeout=5)
    markets = r.json().get('markets', [])
    
    now = datetime.now(timezone.utc)
    crypto_markets = []
    
    for m in markets:
        q = m.get('question', '').lower()
        
        if any(x in q for x in ['bitcoin', 'btc', 'ethereum', 'eth', 'solana', 'sol']):
            # Use correct field names
            current_price = m.get('current_price')
            external_yes = m.get('external_price_yes')
            
            if current_price and external_yes and current_price > 0:
                try:
                    expires_str = m.get('resolves_at', '')
                    expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
                    seconds = (expires_at - now).total_seconds()
                    
                    if seconds > 0:
                        crypto_markets.append({
                            'id': m['id'],
                            'question': m.get('question'),
                            'current_price': float(current_price),
                            'external_yes': float(external_yes),
                            'expires': int(seconds),
                        })
                except:
                    pass
    
    crypto_markets.sort(key=lambda x: x['expires'])
    
    print(f"\n[CRYPTO MARKETS] {len(crypto_markets)} with valid prices")
    
    if not crypto_markets:
        print("No valid markets found!")
    else:
        print("\nTop 5 (nearest expiry):\n")
        for i, m in enumerate(crypto_markets[:5], 1):
            symbol = "BTC" if "btc" in m['question'].lower() else "ETH" if "eth" in m['question'].lower() else "SOL"
            print(f"{i}. [{symbol}] {m['question'][:55]}")
            print(f"   Expires: {m['expires']/3600:.2f}h | Price: ${m['current_price']:.4f}")
        
        # Execute small bites
        print("\n" + "="*80)
        print("EXECUTING: Small diversified bets ($1.50 each)")
        print("="*80)
        
        executed = []
        
        for i, market in enumerate(crypto_markets[:3], 1):
            if balance < 1.50:
                print(f"\nSkip Bet {i}: Insufficient balance")
                break
            
            print(f"\n[Bet {i}]")
            print(f"Market: {market['question'][:60]}")
            
            # BTC/ETH tend UP, SOL is wild - bet accordingly
            symbol = market['question'].lower()
            if 'solana' in symbol:
                side = "no"  # SOL risky, bet down
                logic = "SOL volatile, bet DOWN (safer)"
            else:
                side = "yes"  # BTC/ETH bull market
                logic = "BTC/ETH bull bias, bet UP"
            
            print(f"Bet: $1.50 on {side.upper()} ({logic})")
            
            payload = {
                "market_id": market['id'],
                "side": side,
                "amount_usd": 1.50,
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
                    new_price = response.get('new_price', 0)
                    
                    executed.append({
                        'market': market['question'],
                        'side': side,
                        'amount': 1.50,
                        'trade_id': trade_id,
                        'cost': cost,
                    })
                    
                    print(f"  [EXECUTED] Trade ID: {trade_id}")
                    print(f"  Cost: ${cost:.2f} | New price: ${new_price:.4f}")
                    balance -= cost
                    print(f"  Remaining balance: ${balance:.2f}")
                else:
                    print(f"  [FAILED] {response.get('status', 'unknown error')}")
            
            except Exception as e:
                print(f"  [ERROR] {str(e)[:80]}")
        
        # Summary
        if executed:
            print("\n" + "="*80)
            print("TRADES SUMMARY")
            print("="*80)
            print(f"\nExecuted: {len(executed)} trades")
            total_spent = sum(t['cost'] for t in executed)
            print(f"Total spent: ${total_spent:.2f}")
            print(f"Balance remaining: ${balance:.2f}")
            
            print("\nPositions:")
            for t in executed:
                print(f"  - {t['market'][:50]} | ${t['amount']:.2f} on {t['side'].upper()}")
            
            print(f"\nWin potential: If all hit, return ~${total_spent * 2:.2f} (+${total_spent:.2f} profit)")
            
            # Save for monitoring
            with open('active_trades.json', 'w') as f:
                json.dump(executed, f, indent=2)
        else:
            print("\nNo trades executed")

except Exception as e:
    print(f"\n[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()

print("\n")
