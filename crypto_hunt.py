#!/usr/bin/env python3
"""Hunt BTC, ETH, SOL crypto markets on Simmer for $5-50 profit."""

import requests
import json
from datetime import datetime, timezone

SIMMER_API_KEY = "sk_live_8b62db698791339edac7246d599ee05671f5ad36a0e2b1e2b53e3ceaf7db0cc6"
SIMMER_BASE = "https://api.simmer.markets"

headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}

print("\n" + "="*80)
print("CRYPTO HUNT - BTC, ETH, SOL Markets")
print("="*80)

try:
    r = requests.get(f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=500", 
                    headers=headers, timeout=5)
    markets = r.json().get('markets', [])
    
    now = datetime.now(timezone.utc)
    
    crypto_markets = {
        'btc': [],
        'eth': [],
        'sol': [],
    }
    
    for m in markets:
        q = m.get('question', '').lower()
        
        try:
            expires_str = m.get('resolves_at', '')
            expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
            seconds = (expires_at - now).total_seconds()
            
            # Focus on next 1-6 hours
            if 3600 <= seconds <= 21600:
                yes_p = float(m.get('yes_price', 0.5))
                no_p = float(m.get('no_price', 0.5))
                
                market_obj = {
                    'id': m['id'],
                    'question': m.get('question'),
                    'yes': yes_p,
                    'no': no_p,
                    'expires': int(seconds / 60),
                }
                
                if 'bitcoin' in q or 'btc' in q:
                    crypto_markets['btc'].append(market_obj)
                elif 'ethereum' in q or 'eth' in q:
                    crypto_markets['eth'].append(market_obj)
                elif 'solana' in q or 'sol' in q:
                    crypto_markets['sol'].append(market_obj)
        
        except:
            pass
    
    # Get current prices
    print("\n[CURRENT CRYPTO PRICES]")
    try:
        btc_r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=2)
        btc = float(btc_r.json()['price'])
        print(f"BTC: ${btc:,.2f}")
    except:
        btc = 0
        print("BTC: [error]")
    
    try:
        eth_r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT", timeout=2)
        eth = float(eth_r.json()['price'])
        print(f"ETH: ${eth:,.2f}")
    except:
        eth = 0
        print("ETH: [error]")
    
    try:
        sol_r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=SOLUSDT", timeout=2)
        sol = float(sol_r.json()['price'])
        print(f"SOL: ${sol:,.2f}")
    except:
        sol = 0
        print("SOL: [error]")
    
    # Display markets
    print("\n[BTC MARKETS] " + str(len(crypto_markets['btc'])) + " found")
    if crypto_markets['btc']:
        for m in crypto_markets['btc'][:5]:
            print(f"  {m['question'][:60]}")
            print(f"    Expires: {m['expires']}min | YES: ${m['yes']:.3f} | NO: ${m['no']:.3f}")
    
    print("\n[ETH MARKETS] " + str(len(crypto_markets['eth'])) + " found")
    if crypto_markets['eth']:
        for m in crypto_markets['eth'][:5]:
            print(f"  {m['question'][:60]}")
            print(f"    Expires: {m['expires']}min | YES: ${m['yes']:.3f} | NO: ${m['no']:.3f}")
    
    print("\n[SOL MARKETS] " + str(len(crypto_markets['sol'])) + " found")
    if crypto_markets['sol']:
        for m in crypto_markets['sol'][:5]:
            print(f"  {m['question'][:60]}")
            print(f"    Expires: {m['expires']}min | YES: ${m['yes']:.3f} | NO: ${m['no']:.3f}")
    
    # Get momentum
    print("\n[MOMENTUM SIGNALS] (1-minute candles)")
    try:
        btc_klines = requests.get("https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=10", timeout=2).json()
        btc_open = float(btc_klines[0][1])
        btc_close = float(btc_klines[-1][4])
        btc_change = ((btc_close - btc_open) / btc_open) * 100
        print(f"BTC: {btc_change:+.3f}%")
    except:
        btc_change = 0
        print("BTC: [error]")
    
    try:
        eth_klines = requests.get("https://api.binance.com/api/v3/klines?symbol=ETHUSDT&interval=1m&limit=10", timeout=2).json()
        eth_open = float(eth_klines[0][1])
        eth_close = float(eth_klines[-1][4])
        eth_change = ((eth_close - eth_open) / eth_open) * 100
        print(f"ETH: {eth_change:+.3f}%")
    except:
        eth_change = 0
        print("ETH: [error]")
    
    try:
        sol_klines = requests.get("https://api.binance.com/api/v3/klines?symbol=SOLUSDT&interval=1m&limit=10", timeout=2).json()
        sol_open = float(sol_klines[0][1])
        sol_close = float(sol_klines[-1][4])
        sol_change = ((sol_close - sol_open) / sol_open) * 100
        print(f"SOL: {sol_change:+.3f}%")
    except:
        sol_change = 0
        print("SOL: [error]")
    
    # Opportunity analysis
    print("\n" + "="*80)
    print("OPPORTUNITY ANALYSIS")
    print("="*80)
    
    total_crypto = len(crypto_markets['btc']) + len(crypto_markets['eth']) + len(crypto_markets['sol'])
    print(f"\nTotal crypto markets (1-6hr): {total_crypto}")
    
    if btc_change > 0.3:
        print(f"\n[BULLISH] BTC up {btc_change:+.3f}% in last 1min")
        print("  -> Look for BTC 'will pass X price' markets, bet YES")
    elif btc_change < -0.3:
        print(f"\n[BEARISH] BTC down {btc_change:+.3f}% in last 1min")
        print("  -> Look for BTC 'will pass X price' markets, bet NO")
    else:
        print(f"\n[FLAT] BTC {btc_change:+.3f}% - no strong signal")
    
    print("\nWith $7.96 balance:")
    print("  - Need high-confidence signal + short expiry")
    print("  - Risk/reward: $7.96 all-in could 2x to ~$16")
    print("  - Or split: $2.65 each on 3 different bets")

except Exception as e:
    print("[ERROR] " + str(e))

print("\n")
