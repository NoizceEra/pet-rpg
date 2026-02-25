#!/usr/bin/env python3
"""
UNIFIED SCANNER - "THE BRAIN" (VERSION 1 BACKUP)
Combines FastLoop (Momentum), PBot1 (Arbitrage), and BoyChik (Theoretical Edge) into one efficient loop.
Saved: 2026-02-17
"""

import os
import sys
import json
import time
import math
import logging
import requests
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

# =============================================================================
# Configuration & Constants
# =============================================================================

SIMMER_API_KEY = os.getenv("SIMMER_API_KEY")
SIMMER_BASE = "https://api.simmer.markets"
LOG_FILE = "unified_scanner.log"

# Strategy Settings
FASTLOOP_MOMENTUM_THRESHOLD = 0.5  # 0.5% move
FASTLOOP_LOOKBACK = 5  # minutes
PBOT1_ARB_THRESHOLD = 1.0  # Combined Ask must be < 1.0
BOYCHIK_EDGE_THRESHOLD = 0.05
BTC_VOLATILITY_5M = 0.001

# Logging Setup
# Force UTF-8 for Windows console/logs
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def log(msg):
    try:
        logging.info(msg)
    except Exception as e:
        # Fallback for Windows console if reconfigure fails or encoding issues persist
        print(f"LOG: {msg}".encode('ascii', 'ignore').decode('ascii'))

# =============================================================================
# Core Data Fetchers (Shared)
# =============================================================================

def get_binance_btc_candles(limit=5):
    """Get BTCUSDT candles for momentum calculation."""
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit={limit}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        log(f"Binance Error: {e}")
    return []

def get_vwap_price():
    """Calculate aggregate BTC price from multiple sources for BoyChik."""
    prices = []
    # Binance
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=2).json()
        prices.append(float(r['price']))
    except: pass
    
    # Coinbase
    try:
        r = requests.get("https://api.exchange.coinbase.com/products/BTC-USD/ticker", timeout=2).json()
        prices.append(float(r['price']))
    except: pass

    if not prices:
        return 0.0
    return sum(prices) / len(prices)

def get_active_markets():
    """Fetch active BTC/ETH fast markets via Simmer/Gamma."""
    url = f"{SIMMER_BASE}/api/sdk/markets?tags=fast&status=active&limit=100"
    headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        all_markets = resp.json().get("markets", [])
        
        # Filter for BTC/ETH only
        filtered = []
        for m in all_markets:
            q = m.get('question', '').upper()
            if ('BITCOIN' in q or 'BTC' in q or 'ETHEREUM' in q or 'ETH' in q) and ('UP OR DOWN' in q):
                filtered.append(m)
        
        # Sort by expiration (soonest first)
        filtered.sort(key=lambda x: x.get('resolves_at', ''))
        return filtered
    except Exception as e:
        log(f"Market Discovery Error: {e}")
        return []

def get_clob_price(token_id, side="buy"):
    """Get price from Polymarket CLOB. side='buy' gets Ask (for buying)."""
    if not token_id: return 0.0
    url = f"https://clob.polymarket.com/price?token_id={token_id}&side={side}"
    try:
        resp = requests.get(url, timeout=2)
        data = resp.json()
        return float(data.get("price", 0))
    except:
        return 0.0

# =============================================================================
# Execution Engine
# =============================================================================

def execute_simmer_trade(market_id, side, amount, strategy_name, reasoning):
    url = f"{SIMMER_BASE}/api/sdk/trade"
    headers = {
        "Authorization": f"Bearer {SIMMER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "market_id": market_id,
        "side": side.lower(),
        "amount": amount,
        "venue": "polymarket",
        "source": f"unified:{strategy_name}",
        "reasoning": reasoning
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        res = resp.json()
        if res.get("success"):
            log(f"✅ TRADE EXECUTED ({strategy_name}): {side} on {market_id} for ${amount}")
            return True
        else:
            log(f"❌ TRADE FAILED ({strategy_name}): {res.get('error')}")
            return False
    except Exception as e:
        log(f"Execution Error: {e}")
        return False

# =============================================================================
# Strategy Logic
# =============================================================================

def check_fastloop(candles, markets):
    """
    Momentum Strategy:
    If BTC moves > X% in last 5 mins, bet on continuation if market mispriced.
    """
    if len(candles) < 2: return
    
    start_price = float(candles[0][1])  # Open of oldest candle
    end_price = float(candles[-1][4])   # Close of newest candle
    momentum = ((end_price - start_price) / start_price) * 100
    
    direction = "UP" if momentum > 0 else "DOWN"
    abs_mom = abs(momentum)
    
    log(f"  [FastLoop] Momentum: {momentum:+.4f}% ({direction})")
    
    if abs_mom < FASTLOOP_MOMENTUM_THRESHOLD:
        return  # No strong signal

    # Find best market
    for m in markets:
        # Simple heuristic: Only look at next expiring 5m market
        if "5:30" in m['question'] or "5:35" in m['question']: # Placeholder for precise time parsing
             # Real implementation would parse end_time properly
             pass
    
    # (Simplified for Unified Scan - currently reporting only)
    if abs_mom >= FASTLOOP_MOMENTUM_THRESHOLD:
        log(f"  ⚡ FastLoop Signal Active! {direction} momentum > {FASTLOOP_MOMENTUM_THRESHOLD}%")

def check_pbot1_arb(markets):
    """
    Arbitrage Strategy:
    Check if Ask(Yes) + Ask(No) < 1.00 (Guaranteed profit).
    """
    log("  [PBot1] Scanning for Arbs...")
    for m in markets[:5]:  # Check top 5 soonest
        yes_id = m.get("polymarket_token_id")
        no_id = m.get("polymarket_no_token_id")
        
        ask_yes = get_clob_price(yes_id, "buy")
        ask_no = get_clob_price(no_id, "buy")
        
        if ask_yes > 0 and ask_no > 0:
            combined = ask_yes + ask_no
            if combined < 1.0:
                profit = (1.0 - combined) * 100
                log(f"  🚨 ARB FOUND! {m['question']} | Cost: {combined:.4f} | Profit: {profit:.2f}%")
                execute_simmer_trade(m['id'], "yes", 5.0, "pbot1", "Arb")
                execute_simmer_trade(m['id'], "no", 5.0, "pbot1", "Arb")
                return # Take one arb per cycle to avoid rate limits

def check_boychik(vwap, markets):
    """
    Theoretical Edge Strategy:
    Compare current market probability vs theoretical probability derived from Volatility + Time.
    """
    log(f"  [BoyChik] VWAP: ${vwap:,.2f}")
    # (Simplified logic from original script)
    # Check first BTC market
    for m in markets:
        if "BITCOIN" not in m['question'].upper(): continue
        
        # Parse strike (very basic regex)
        import re
        match = re.search(r'(\d{5})', m['question'])
        if match:
            strike = float(match.group(1))
            # Basic edge logic placeholder
            # Real impl needs time_to_expiry calc
            pass

# =============================================================================
# Main Loop
# =============================================================================

def run_unified_scan():
    log("--- 🧠 Unified Scanner Initiated ---")
    
    # 1. Fetch Data Once
    markets = get_active_markets()
    log(f"Found {len(markets)} active markets.")
    
    if not markets:
        log("No markets found. Exiting.")
        return

    candles = get_binance_btc_candles()
    vwap = get_vwap_price()
    
    # 2. Run Strategies
    check_fastloop(candles, markets)
    check_pbot1_arb(markets)
    check_boychik(vwap, markets)
    
    log("--- Scan Complete ---")

if __name__ == "__main__":
    log("--- 🚀 STARTING UNIFIED SCANNER LOOP (60s interval) ---")
    while True:
        try:
            run_unified_scan()
        except Exception as e:
            log(f"CRITICAL ERROR in main loop: {e}")
        
        # Sleep 60 seconds before next scan
        time.sleep(60)
