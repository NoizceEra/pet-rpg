import os
import requests
import json
from datetime import datetime

SIMMER_API_KEY = os.getenv("SIMMER_API_KEY")

def log(msg):
    print(f"[{datetime.now()}] {msg}", flush=True)

def liquidate_tomorrow():
    log("Liquidating tomorrow's (Feb 17) positions...")
    
    # 1. Get current positions via Simmer
    url = "https://api.simmer.markets/api/sdk/positions?venue=polymarket"
    headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        positions = resp.json().get("positions", [])
        
        liquidated_count = 0
        for pos in positions:
            question = pos.get("question", "").upper()
            if "FEBRUARY 17" in question:
                market_id = pos.get("market_id")
                side = pos.get("side")
                shares = float(pos.get("shares", 0))
                
                if shares > 0:
                    log(f"Liquidating {shares} shares of {side} on '{question}'")
                    
                    # 2. Sell position
                    sell_url = "https://api.simmer.markets/api/sdk/trades"
                    payload = {
                        "market_id": market_id,
                        "side": side,
                        "shares": shares,
                        "action": "sell",
                        "venue": "polymarket"
                    }
                    sell_resp = requests.post(sell_url, json=payload, headers=headers, timeout=30)
                    if sell_resp.json().get("success"):
                        log(f"SUCCESS: Liquidated {market_id}")
                        liquidated_count += 1
                    else:
                        log(f"FAILED: {sell_resp.json().get('error')}")
        
        log(f"Liquidation complete. Total positions closed: {liquidated_count}")
        
    except Exception as e:
        log(f"Liquidation Error: {e}")

if __name__ == "__main__":
    liquidate_tomorrow()
