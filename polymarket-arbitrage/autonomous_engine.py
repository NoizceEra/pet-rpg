#!/usr/bin/env python3
"""
Autonomous execution engine for Polymarket Arbitrage & Strategy.
V2.4 - SILENT MODE (Zero-Notification Background Scanning)
Saves credits by logging everything to forensics instead of pinging Telegram.
"""

import json
import time
import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows encoding issues
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds

load_dotenv()

# Constants
MAX_POSITION_SIZE = 5.60  # USD per leg
MIN_NET_EDGE = 3.0       # %
TAKER_FEE = 0.02
HOST = "https://clob.polymarket.com"
CHAIN_ID = 137

# Workspace Paths
WORKSPACE_DIR = Path(r"C:\Users\vclin_jjufoql\.openclaw\workspace\polymarket-arbitrage")
FORENSICS_DIR = WORKSPACE_DIR / "forensics"

def get_client():
    creds = ApiCreds(
        api_key=os.getenv("POLYMARKET_API_KEY"),
        api_secret=os.getenv("POLYMARKET_API_SECRET"),
        api_passphrase=os.getenv("POLYMARKET_API_PASSPHRASE")
    )
    return ClobClient(host=HOST, key=os.getenv("POLYMARKET_PRIVATE_KEY"), chain_id=CHAIN_ID, creds=creds)

def calculate_risk_score(net_profit_pct, leg_count):
    score = 40
    if net_profit_pct > 15: score += 20
    elif net_profit_pct > 5: score -= 10
    if leg_count > 2: score += (leg_count - 2) * 5
    return max(0, min(100, score))

def log_trade(market_name, strategy, size, risk_score, details=None):
    """Silent logging to Forensics folder. NO Telegram pings."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "market": market_name,
        "strategy": strategy,
        "size": size,
        "status": "PAPER_ENTERED",
        "risk_score": risk_score,
        "details": details
    }
    
    # Save to forensics with UTF-8 encoding
    filename = f"trade_{strategy}_{int(time.time() * 1000)}.json"
    try:
        with open(FORENSICS_DIR / filename, "w", encoding='utf-8') as f:
            json.dump(entry, f, indent=2)
    except Exception as e:
        print(f"Logging error: {e}")

def strategy_math_arb(client, market):
    tokens = market.get('tokens', [])
    if len(tokens) < 2: return
    
    prices = [t.get('price') for t in tokens if t.get('price') is not None]
    if len(prices) < len(tokens): return
    
    prob_sum = sum(prices) * 100
    if prob_sum < 100:
        net_profit = (100 - prob_sum) - (TAKER_FEE * 100 * len(tokens))
        if net_profit >= MIN_NET_EDGE:
            score = calculate_risk_score(net_profit, len(tokens))
            legs = [{"outcome": t['outcome'], "price": t['price']} for t in tokens]
            log_trade(market['question'], "math_arb", MAX_POSITION_SIZE * len(tokens), score, 
                     {"profit": net_profit, "prob_sum": prob_sum, "legs": legs})

def strategy_risk_harvesting(client, market):
    tokens = market.get('tokens', [])
    for token in tokens:
        price = token.get('price')
        if price is not None and price < 0.02:
            log_trade(market['question'], "risk_harvest", MAX_POSITION_SIZE, 15, 
                     {"outcome": token['outcome'], "price": price})

def main_loop():
    client = get_client()
    print("Engine V2.4 - SILENT MODE (Zero-Notification Background Scanning)")
    
    while True:
        try:
            resp = client.get_sampling_markets()
            markets = resp.get('data', []) if isinstance(resp, dict) else []
            
            if not markets:
                time.sleep(10)
                continue

            print(f"[{datetime.now().strftime('%H:%M:%S')}] Scanned {len(markets)} markets.")
            
            for m in markets:
                try:
                    strategy_math_arb(client, m)
                    strategy_risk_harvesting(client, m)
                except Exception:
                    pass
            
        except Exception as e:
            print(f"Engine Error: {e}")
            
        time.sleep(30)

if __name__ == "__main__":
    FORENSICS_DIR.mkdir(exist_ok=True)
    main_loop()
