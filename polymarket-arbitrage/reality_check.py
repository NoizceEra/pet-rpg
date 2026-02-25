#[!]/usr/bin/env python3
"""
REALITY CHECK: Are there actually arbitrage opportunities RIGHT NOW?

Tests:
1. Can we connect to Polymarket API?
2. Are there any markets with orderbook data?
3. Do any real arbitrages exist (using ask prices, not midpoints)?
4. What's the edge after fees?
"""

import os
import json
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds

load_dotenv()

# Setup client
creds = ApiCreds(
    api_key=os.getenv("POLYMARKET_API_KEY"),
    api_secret=os.getenv("POLYMARKET_API_SECRET"),
    api_passphrase=os.getenv("POLYMARKET_API_PASSPHRASE")
)

client = ClobClient(
    host="https://clob.polymarket.com",
    key=os.getenv("POLYMARKET_PRIVATE_KEY"),
    chain_id=137,
    creds=creds
)

print("=" * 60)
print("POLYMARKET ARBITRAGE REALITY CHECK")
print("=" * 60)
# Test 1: Get sampling markets
print("\n[1/4] Fetching markets...")
try:
    resp = client.get_sampling_markets()
    markets = resp.get('data', []) if isinstance(resp, dict) else []
    print(f"[OK] Found {len(markets)} markets")
except Exception as e:
    print(f"[FAIL] Failed to fetch markets: {e}")
    exit(1)

# Test 2: Check for orderbook data
print("\n[2/4] Checking orderbook availability...")
test_count = 0
orderbook_count = 0

for market in markets[:5]:  # Test first 5
    tokens = market.get('tokens', [])
    if not tokens:
        continue
    
    test_count += 1
    token_id = tokens[0].get('token_id')
    
    if token_id:
        try:
            book = client.get_order_book(token_id)
            if book and (book.get('bids') or book.get('asks')):
                orderbook_count += 1
        except:
            pass

print(f"[OK] {orderbook_count}/{test_count} test markets have orderbook data")
# Test 3: Look for real arbitrages (using ASK prices)
print("\n[3/4] Scanning for REAL arbitrage (using ask prices)...")
arb_count = 0
TAKER_FEE = 0.02

for market in markets[:50]:  # Check first 50
    tokens = market.get('tokens', [])
    if len(tokens) < 2:
        continue
    
    # Get best ask for each outcome
    ask_prices = []
    for token in tokens:
        token_id = token.get('token_id')
        if not token_id:
            continue
        
        try:
            book = client.get_order_book(token_id)
            if book and book.get('asks'):
                # Best ask is what we PAY to buy
                best_ask = float(book['asks'][0]['price'])
                ask_prices.append(best_ask)
        except:
            break
    
    # Check if we can profit by buying all outcomes
    if len(ask_prices) == len(tokens):
        total_cost = sum(ask_prices)
        total_fees = TAKER_FEE * len(ask_prices)
        net_profit = 1.0 - (total_cost + total_fees)
        net_profit_pct = net_profit * 100
        
        if net_profit_pct >= 2.0:  # Min 2% edge
            arb_count += 1
            print(f"\n  ARBITRAGE FOUND[!]")
            print(f"    Market: {market.get('question', 'Unknown')[:60]}...")
            print(f"    Ask prices: {[f'${p:.3f}' for p in ask_prices]}")
            print(f"    Total cost: ${total_cost:.3f}")
            print(f"    Net profit: {net_profit_pct:.2f}%")

print(f"\n[OK] Found {arb_count} real arbitrage opportunities")
# Test 4: Current balance
print("\n[4/4] Checking account status...")
try:
    balance = client.get_balance()
    print(f"[OK] USDC Balance: ${float(balance):,.2f}")
except Exception as e:
    print(f"[!] Could not fetch balance: {e}")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Markets available: {len(markets)}")
print(f"Markets with orderbooks: {orderbook_count}/{test_count} tested")
print(f"Real arbitrages found: {arb_count}")

if arb_count > 0:
    print("\n[SUCCESS] ARBITRAGE EXISTS - Bot could potentially profit")
    print("   Next step: Fix execution engine to actually place orders")
else:
    print("\n[WARN]  NO ARBITRAGE FOUND")
    print("   Possible reasons:")
    print("   - Markets are efficient (no free money)")
    print("   - Need to scan more markets")
    print("   - Need faster execution (arbs close quickly)")
    print("   - Minimum edge threshold too high")

print("=" * 60)
