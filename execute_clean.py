#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Execute real trades - longer timeout, clean encoding."""

import requests
import json
from datetime import datetime, timezone

NEW_KEY = "sk_live_484943fcabd5d3dd5e58106872e6831aedbd340139736760dc10773c47471570"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {NEW_KEY}"}

print("\n" + "="*80)
print("FINAL EXECUTION - Longer Timeout")
print("="*80)

try:
    # Get portfolio
    r = requests.get(f"{SIMMER_BASE}/api/sdk/portfolio", 
                    headers=headers, timeout=10)
    balance = float(r.json().get('balance_usdc', 0))
    
    print("\n[BALANCE] $" + f"{balance:.2f}")
    
    # Get markets
    r = requests.get(f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=500", 
                    headers=headers, timeout=10)
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
    
    print("[CRYPTO MARKETS] " + str(len(crypto_markets)) + " with valid prices")
    
    if crypto_markets:
        print("\nTop 3:\n")
        for i, m in enumerate(crypto_markets[:3], 1):
            symbol = "BTC" if "btc" in m['question'].lower() else "ETH" if "eth" in m['question'].lower() else "SOL"
            print(str(i) + ". [" + symbol + "] " + m['question'][:50])
            print("   Expires: " + f"{m['expires']/3600:.1f}" + "h")
        
        print("\n" + "="*80)
        print("DEPLOYING: $1.50 x 3 SMALL BETS")
        print("="*80)
        
        executed = []
        
        for i, market in enumerate(crypto_markets[:3], 1):
            if balance < 1.50:
                print("\nBet " + str(i) + ": Insufficient balance")
                break
            
            print("\n[Bet " + str(i) + "]")
            print("Market: " + market['question'][:50])
            
            if 'solana' in market['question'].lower():
                side = "no"
            else:
                side = "yes"
            
            print("Bet: $1.50 on " + side.upper())
            
            payload = {
                "market_id": market['id'],
                "side": side,
                "amount": 1.50,
            }
            
            try:
                r = requests.post(f"{SIMMER_BASE}/api/sdk/trade",
                                 headers=headers,
                                 json=payload,
                                 timeout=15)
                
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
                    
                    print("EXECUTED | Trade ID: " + str(trade_id))
                    print("Cost: $" + f"{cost:.2f}" + " | Remaining: $" + f"{balance:.2f}")
                else:
                    error = response.get('error', 'unknown')
                    print("FAILED | " + str(error)[:80])
            
            except Exception as e:
                print("ERROR | " + str(e)[:80])
        
        if executed:
            print("\n" + "="*80)
            print("SUCCESS - " + str(len(executed)) + " Trades Executed")
            print("="*80)
            
            total = sum(t['amount'] for t in executed)
            print("\nDeployed: $" + f"{total:.2f}")
            print("Remaining: $" + f"{balance:.2f}")
            
            print("\nPositions:")
            for t in executed:
                print("  - " + t['market'][:45] + " | $" + f"{t['amount']:.2f}" + " on " + t['side'].upper())
            
            print("\nIf all hit: Return ~$" + f"{total * 2:.2f}" + " (+$" + f"{total:.2f}" + " profit)")
            
            with open('active_trades.json', 'w') as f:
                json.dump(executed, f, indent=2)
            
            print("\nSaved to active_trades.json")
        else:
            print("\nNo trades executed")

except Exception as e:
    print("\n[ERROR] " + str(e))

print("\n")
