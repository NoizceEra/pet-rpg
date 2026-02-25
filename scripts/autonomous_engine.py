import os
import time
import json
import requests
import sys
from datetime import datetime, timezone

# Force unbuffered output for cleaner logs
def log(msg):
    print(f"[{datetime.now()}] {msg}", flush=True)

# Configuration
SIMMER_API_KEY = os.getenv("SIMMER_API_KEY")
MIN_SHARES = 10  # Buying 10 shares of each side
POLL_INTERVAL = 3  # Seconds between checks
MAX_COMBINED_PRICE = 0.99  # Capture $0.01 profit per share minimum

def get_active_sprint_markets():
    """Fetch 15m and 5m crypto sprint markets."""
    url = "https://api.simmer.markets/api/sdk/markets?tags=fast&status=active&limit=20"
    headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        return resp.json().get("markets", [])
    except Exception as e:
        log(f"Discovery Error: {e}")
        return []

def get_clob_price(token_id):
    """Get the current best midpoint price from Polymarket CLOB."""
    url = f"https://clob.polymarket.com/midpoint?token_id={token_id}"
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if "mid" in data:
            return float(data["mid"])
        return 0
    except:
        return 0

def execute_arb(market_id, combined_price):
    """Execute buy on BOTH sides via Simmer Market Orders."""
    url = "https://api.simmer.markets/api/sdk/trades/batch"
    headers = {
        "Authorization": f"Bearer {SIMMER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "trades": [
            {"market_id": market_id, "side": "yes", "amount": 6.0},
            {"market_id": market_id, "side": "no", "amount": 6.0}
        ],
        "venue": "polymarket",
        "source": "micro-arb:pbot1"
    }
    
    log(f"SEIZING ARB: Combined Price ${combined_price:.3f}. Executing batch...")
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        result = resp.json()
        if result.get("success"):
            log(f"SUCCESS: Arb captured on {market_id}")
            with open("arb_wins.log", "a") as f:
                f.write(f"{datetime.now()} | {market_id} | Combined: {combined_price}\n")
        else:
            log(f"Trade Failed: {result.get('error')}")
    except Exception as e:
        log(f"Execution Error: {e}")

def run():
    log("Micro-Arb Engine Started (Autonomy: HOOL)")
    while True:
        try:
            markets = get_active_sprint_markets()
            if not markets:
                time.sleep(10)
                continue

            for m in markets:
                yes_token = m.get("polymarket_token_id")
                no_token = m.get("polymarket_no_token_id")
                
                if not yes_token or not no_token:
                    continue
                    
                price_yes = get_clob_price(yes_token)
                price_no = get_clob_price(no_token)
                
                if price_yes > 0 and price_no > 0:
                    combined = price_yes + price_no
                    if combined < MAX_COMBINED_PRICE:
                        execute_arb(m['id'], combined)
            
            time.sleep(POLL_INTERVAL)
        except Exception as e:
            log(f"Main Loop Exception: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run()
