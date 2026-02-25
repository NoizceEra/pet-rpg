#!/usr/bin/env python3
"""
UNIFIED SCANNER - "THE BRAIN"
Combines FastLoop (Momentum), PBot1 (Arbitrage), and BoyChik (Theoretical Edge) into one efficient loop.
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

# Strategy Settings (BALANCED MODE - Updated 2026-02-20 14:45)
FASTLOOP_MOMENTUM_THRESHOLD = 0.8  # 0.8% move (STRICTER - was 0.5%)
FASTLOOP_LOOKBACK = 5  # minutes
PBOT1_ARB_THRESHOLD = 0.96  # Combined Ask must be < 0.96 (4% profit buffer - STRICTER)
MASSIVE_GAIN_THRESHOLD = 0.30 # 10-30% ROI range = Take Profit window
MIN_TAKE_PROFIT = 0.10  # Min 10% ROI to exit
MAX_TAKE_PROFIT = 0.30  # Max 30% ROI target
BOYCHIK_EDGE_THRESHOLD = 0.05
BTC_VOLATILITY_5M = 0.001
RESERVE_AMOUNT = 1.0  # Protect Capital baseline
MAX_DAILY_TRADES = 100  # High frequency enabled
PROFIT_WITHDRAWAL_THRESHOLD = 20.0  # Auto-withdraw when daily profit hits $20

# Logging Setup
# Force UTF-8 for Windows console/logs
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Ensure log file path is absolute or handled correctly
LOG_PATH = os.path.join(os.getcwd(), LOG_FILE)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH, encoding='utf-8'),
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
    url = f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=100"
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

def get_usdc_balance():
    """Fetch available USDC balance from Simmer Portfolio."""
    url = f"{SIMMER_BASE}/api/sdk/portfolio"
    headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        data = resp.json()
        # Parse balance_usdc
        balance = data.get("balance_usdc")
        if balance is None:
            return 0.0 # No wallet linked or error
        return float(balance)
    except Exception as e:
        log(f"Balance Check Error: {e}")
        return 10.0 # Safe fallback during dev to keep running

def calculate_size(strategy, balance):
    """
    Dynamic Sizing Logic (CONSERVATIVE - Updated 2026-02-20)
    "Small profits win the race" - User directive
    - PBot1 Arb: 15% max (was 35%)
    - FastLoop: 5% max
    - Other: 3% max (was 5%)
    """
    # 1. Check Hard Reserve
    available_liquidity = balance - RESERVE_AMOUNT
    if available_liquidity < 2.0: # Minimum trade floor (increased from 1.05)
        return 0.0

    # 2. Calculate Base Size (CONSERVATIVE)
    if balance < 50.0:
        # Conservative Growth
        raw_size = balance * 0.15  # REDUCED from 0.35
    elif strategy == "pbot1": 
        raw_size = balance * 0.15  # REDUCED from 0.35 (even arbs use less capital)
    else: 
        raw_size = balance * 0.03  # REDUCED from 0.05 
        
    # 3. Apply Limits
    size = max(1.05, raw_size)    
    size = min(size, available_liquidity) 
    
    # 4. Share Floor Safety
    # Polymarket requires 5 shares minimum. 
    # If size / 0.99 (max cost) < 5, we can't trade.
    if size < 5.0: # Conservatively assuming $1.00 shares; actually tighter but this is safe
         # Check if we can push up to 5 shares with available liquidity
         if available_liquidity >= 5.0:
             size = 5.05 # Push to clear floor
         else:
             return 0.0 # Not enough liquidity to hit share floor
    
    max_market_size = 7.00 # USD limit per market

# ... inside calculate_size function ...
    if strategy != "pbot1" and balance > 50:
        size = min(size, max_market_size)
    
    # ... rest of the function ...
    
    return round(size, 2)

# =============================================================================
# Execution Engine
# =============================================================================

def execute_simmer_trade(market_id, side, amount, strategy_name, reasoning, action="buy", shares=None):
    if action == "buy":
        # Pre-Trade Balance Check (Double Safety)
        for attempt in range(2):
            try:
                url_bal = f"{SIMMER_BASE}/api/sdk/portfolio"
                resp_bal = requests.get(url_bal, headers={"Authorization": f"Bearer {SIMMER_API_KEY}"}, timeout=5)
                if resp_bal.status_code == 200:
                    curr_bal = float(resp_bal.json().get("balance_usdc", 0))
                    break
            except Exception as e:
                log(f"⚠️ Balance check attempt {attempt+1} failed ({e}).")
                if attempt == 0: time.sleep(1)
        else:
            curr_bal = 0.0 # Fallback
            
        # Re-verify sizing against current balance (microseconds matter in crypto)
        safe_size = calculate_size(strategy_name, curr_bal)
        
        if safe_size == 0.0:
            log(f"🛑 Trade Aborted: Balance ${curr_bal:.2f} too close to reserve ${RESERVE_AMOUNT}")
            return False
            
        if amount > safe_size:
            log(f"⚠️ Sizing Adjustment: Lowering trade from ${amount} to ${safe_size} to protect reserve.")
            amount = safe_size

    url = f"{SIMMER_BASE}/api/sdk/trade"
    headers = {
        "Authorization": f"Bearer {SIMMER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "market_id": market_id,
        "side": side.lower(),
        "venue": "polymarket",
        "source": f"unified:{strategy_name}",
        "reasoning": reasoning,
        "action": action
    }
    
    if action == "buy":
        payload["amount"] = amount
    else:
        payload["shares"] = shares

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        res = resp.json()
        if res.get("success"):
            log(f"✅ TRADE EXECUTED ({strategy_name} {action.upper()}): {side} on {market_id}")
            return True
        else:
            log(f"❌ TRADE FAILED ({strategy_name} {action.upper()}): {res.get('error')}")
            return False
    except Exception as e:
        log(f"Execution Error: {e}")
        return False

# =============================================================================
# Strategy Logic
# =============================================================================

def run_market_discovery():
    """Fetches active markets (slow, API heavy)."""
    markets = get_active_markets()
    log(f"Discovery: Found {len(markets)} active markets.")
    return markets

def run_price_check_loop(markets):
    """Fast loop (5s) for price checks."""
    try:
        # Update balance (fast)
        url = f"{SIMMER_BASE}/api/sdk/portfolio"
        resp = requests.get(url, headers={"Authorization": f"Bearer {SIMMER_API_KEY}"}, timeout=2)
        usdc_balance = float(resp.json().get("balance_usdc", 10.0))
    except:
        usdc_balance = 10.0 # Fallback

    candles = get_binance_btc_candles(limit=5) # Ensure enough candles for momentum
    
    # Run Checks
    check_fastloop(candles, markets, usdc_balance)
    check_pbot1_arb(markets, usdc_balance)

def get_current_positions():
    """Fetch active positions from Simmer with robust error handling."""
    url = f"{SIMMER_BASE}/api/sdk/positions"
    headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}
    for attempt in range(2): # Quick retry
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                return resp.json().get("positions", [])
        except Exception as e:
            log(f"Position Check Attempt {attempt+1} Error: {e}")
            if attempt == 0: time.sleep(1)
    return []

def check_active_positions_for_exits():
    """Scan positions for ROI > threshold and liquidate. Also auto-redeems winners."""
    log("  [Hungry Mode] Checking positions for profit/redemption...")
    url = f"{SIMMER_BASE}/api/sdk/positions"
    headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        positions = resp.json().get("positions", [])
        
        for p in positions:
            # 1. Auto-Redeem Winning Shares
            if p.get("redeemable"):
                log(f"  🏆 WINNER DETECTED! Redeeming {p['question']}...")
                side = "yes" if p.get("shares_yes", 0) > 0 else "no"
                requests.post(f"{SIMMER_BASE}/api/sdk/redeem", json={"market_id": p['market_id'], "side": side}, headers=headers)
                continue

            # 2. Aggressive Take Profit
            pnl = p.get("pnl", 0)
            cost_basis = p.get("cost_basis", 1)
            roi = pnl / cost_basis if cost_basis > 0.01 else 0
            
            # Limit ROI reporting to sane levels to detect bugs
            if roi > 5.0:
                log(f"  ⚠️ Warning: ROI calculation anomaly detected ({roi*100:.1f}%). Market: {p['question']}. PNL: {pnl}, Cost: {cost_basis}")
                continue

            if roi >= MASSIVE_GAIN_THRESHOLD:
                log(f"  💰 HUNGRY TP HIT! ROI: {roi*100:.1f}% on {p['question']}. Taking the money!")
                if p.get("shares_yes", 0) > 0:
                    execute_simmer_trade(p['market_id'], "yes", 0, "exits", "Hungry TP", action="sell", shares=p['shares_yes'])
                if p.get("shares_no", 0) > 0:
                    execute_simmer_trade(p['market_id'], "no", 0, "exits", "Hungry TP", action="sell", shares=p['shares_no'])
    except Exception as e:
        log(f"Exit/Redeem Error: {e}")

def check_fastloop(candles, markets, balance):
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

    # Calculate Size
    size = calculate_size("fastloop", balance)
    
    if size <= 0:
        log(f"  ⚠️ Signal Active but Liquidity Low. Reserve: ${RESERVE_AMOUNT}. Skipping.")
        return

    log(f"  ⚡ FastLoop Signal Active! {direction} > {FASTLOOP_MOMENTUM_THRESHOLD}%. Sizing: ${size:.2f}")

    # Execution: Find first BTC market and trade direction
    target_market = None
    for m in markets:
        if "Bitcoin" in m.get('question', '') or "BTC" in m.get('question', ''):
            target_market = m
            break
            
    if target_market:
        # Map Direction to Side
        # "Will Bitcoin be above X?" -> UP = Yes, DOWN = No
        # (Assuming standard "Above" phrasing for active markets)
        side = "yes" if direction == "UP" else "no"
        
        log(f"  🎯 FastLoop Executing: {side.upper()} on {target_market['question']}")
        execute_simmer_trade(target_market['id'], side, size, "fastloop", f"Momentum {direction}")
    else:
        log("  ❌ FastLoop Signal but no BTC market found.")

def check_pbot1_arb(markets, balance):
    """
    Arbitrage Strategy:
    Check if Ask(Yes) + Ask(No) < 0.98 (Guaranteed profit).
    """
    log("  [PBot1] Scanning for Arbs...")
    
    # Calculate Size
    size = calculate_size("pbot1", balance)
    
    if size <= 0:
        return # Skip logging if we can't trade

    # Get current positions to avoid re-arbing
    positions = get_current_positions()
    arbed_market_ids = {p['market_id'] for p in positions if (p.get('shares_yes', 0) > 1.0 or p.get('shares_no', 0) > 1.0)} # Changed to ANY position in market

    for m in markets[:5]:  # Check top 5 soonest
        if m['id'] in arbed_market_ids:
            # log(f"  ⏭️ Skipping {m['id']} - already have position.")
            continue # Already have a stake here
            
        yes_id = m.get("polymarket_token_id")
        no_id = m.get("polymarket_no_token_id")
        
        ask_yes = get_clob_price(yes_id, "buy")
        ask_no = get_clob_price(no_id, "buy")
        
        if ask_yes > 0 and ask_no > 0:
            combined = ask_yes + ask_no
            if combined < PBOT1_ARB_THRESHOLD:
                profit = (1.0 - combined) * 100
                log(f"  🚨 ARB FOUND! {m['question']} | Cost: {combined:.4f} | Profit: {profit:.2f}% | Size: ${size:.2f}")
                execute_simmer_trade(m['id'], "yes", size, "pbot1", "Arb")
                execute_simmer_trade(m['id'], "no", size, "pbot1", "Arb")
                return # Take one arb per cycle to avoid rate limits

def check_boychik(vwap, markets, balance):
    """
    Theoretical Edge Strategy: Placeholder
    """
    pass

# =============================================================================
# Main Loop
# =============================================================================

if __name__ == "__main__":
    log("--- 🚀 STARTING UNIFIED SCANNER LOOP (Split Discovery/Check) ---")
    
    cached_markets = []
    last_discovery = 0
    last_exit_check = 0
    DISCOVERY_INTERVAL = 60
    EXIT_CHECK_INTERVAL = 30
    CHECK_INTERVAL = 5
    
    while True:
        now = time.time()
        
        # 1. Market Discovery (Slow)
        if now - last_discovery > DISCOVERY_INTERVAL or not cached_markets:
            try:
                cached_markets = run_market_discovery()
                last_discovery = time.time()
            except Exception as e:
                log(f"Discovery Error: {e}")
        
        # 2. Exit Checks (Medium)
        if now - last_exit_check > EXIT_CHECK_INTERVAL:
            try:
                check_active_positions_for_exits()
                last_exit_check = time.time()
            except Exception as e:
                log(f"Exit Check Error: {e}")

        # 3. Price Checks (Fast)
        if cached_markets:
            try:
                run_price_check_loop(cached_markets)
            except Exception as e:
                log(f"Check Loop Error: {e}")
        
        # Sleep short
        time.sleep(CHECK_INTERVAL)
