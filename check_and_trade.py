#!/usr/bin/env python3
"""Check status and force a trade if conditions met."""

import requests
import json
from datetime import datetime, timezone

SIMMER_API_KEY = "sk_live_8b62db698791339edac7246d599ee05671f5ad36a0e2b1e2b53e3ceaf7db0cc6"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}

print("\n" + "="*70)
print("CHECKING STATUS...")
print("="*70)

# Get BTC markets
try:
    r = requests.get(f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=100", 
                    headers=headers, timeout=3)
    markets = r.json().get('markets', [])
    
    now = datetime.now(timezone.utc)
    valid = []
    
    for m in markets:
        q = m.get('question', '').upper()
        if 'bitcoin' not in q and 'btc' not in q:
            continue
        
        try:
            expires_str = m.get('resolves_at', '')
            expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
            seconds = (expires_at - now).total_seconds()
            
            if 300 <= seconds <= 900:
                valid.append({
                    'id': m['id'],
                    'question': m.get('question', ''),
                    'expires': int(seconds),
                    'obj': m,
                })
        except:
            pass
    
    valid.sort(key=lambda x: x['expires'])
    
    if valid:
        print("[OK] BTC 5-15min markets available: " + str(len(valid)))
        for v in valid[:3]:
            print("   " + v['question'][:60] + " | " + str(v['expires']) + "s")
    else:
        print("[NONE] No BTC 5-15min windows available")

except Exception as e:
    print("[ERROR] Market fetch: " + str(e))
    valid = []

# Get BTC momentum
try:
    url = f"https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=5"
    r = requests.get(url, timeout=3)
    candles = r.json()
    
    momentum = 0
    direction = None
    change = 0
    btc_price = 0
    
    if len(candles) >= 2:
        open_p = float(candles[0][1])
        close_p = float(candles[-1][4])
        change = ((close_p - open_p) / open_p) * 100
        momentum = abs(change)
        direction = "UP" if change > 0 else "DOWN"
        btc_price = close_p
        
        status = "OK" if momentum >= 0.5 else "LOW"
        print("[" + status + "] BTC Momentum: " + f"{change:+.3f}%" + " (" + direction + ") | Price: $" + f"{btc_price:.2f}")

except Exception as e:
    print("[ERROR] Momentum: " + str(e))
    momentum = 0

# Check balance
try:
    r = requests.get(f"{SIMMER_BASE}/api/sdk/portfolio", headers=headers, timeout=3)
    balance = float(r.json().get('balance_usdc', 0.0))
    print("[OK] Balance: $" + f"{balance:.2f}")
except Exception as e:
    print("[ERROR] Balance: " + str(e))
    balance = 0

# Can we trade?
print("\n" + "="*70)
can_trade = valid and momentum >= 0.5 and balance >= 15

if can_trade:
    print("READY - EXECUTING TRADE")
    print("="*70)
    
    market = valid[0]
    side = "yes" if direction == "UP" else "no"
    size = min(balance * 0.10, 150)
    size = max(size, 15)
    
    print("\nMarket: " + market['question'][:60])
    print("Expires: " + str(market['expires']) + "s")
    print("BTC Signal: " + f"{change:+.3f}%" + " " + direction)
    print("Side: " + side.upper())
    print("Size: $" + f"{size:.2f}")
    
    try:
        payload = {
            "market_id": market['id'],
            "side": side,
            "amount_usd": size,
        }
        
        r = requests.post(f"{SIMMER_BASE}/api/sdk/trade", 
                         headers=headers, json=payload, timeout=5)
        
        if r.status_code in [200, 201]:
            print("\n[EXECUTED]")
            result = r.json()
            print("Trade ID: " + str(result.get('id')))
            print("Entry Price: $" + f"{result.get('price', 0):.4f}")
        else:
            print("\n[FAILED] Status: " + str(r.status_code))
            print(r.text[:200])
    
    except Exception as e:
        print("\n[ERROR] Execution: " + str(e))

else:
    print("BLOCKED - CANNOT TRADE")
    print("="*70)
    print("Markets available: " + str(len(valid) > 0))
    print("Momentum high enough: " + str(momentum >= 0.5) + " (need 0.5%, have " + f"{momentum:.3f}%" + ")")
    print("Balance sufficient: " + str(balance >= 15) + " (need 15, have $" + f"{balance:.2f}" + ")")

print("\n")
