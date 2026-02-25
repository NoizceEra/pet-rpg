import os
import requests
import json
import time
from datetime import datetime
from pathlib import Path

SIMMER_API_KEY = os.getenv("SIMMER_API_KEY")
WALLET_ADDRESS = "0x88f46b9e5d86b4fb85be55ab0ec4004264b9d4db"
STATE_FILE = Path("pbot1_positions_state.json")

def log(msg):
    print(f"[{datetime.now()}] {msg}", flush=True)

def get_positions():
    url = f"https://api.simmer.markets/api/sdk/wallet/{WALLET_ADDRESS}/positions"
    headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        return resp.json()
    except Exception as e:
        log(f"Error fetching positions: {e}")
        return None

def monitor():
    log(f"Checking @PBot1 ({WALLET_ADDRESS}) positions...")
    data = get_positions()
    if not data or "positions" not in data:
        log("Failed to fetch positions.")
        return

    current_positions = data["positions"]
    
    # Load previous state
    previous_positions = {}
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r") as f:
                previous_positions = json.load(f)
        except:
            pass

    # Compare
    new_trades = []
    current_state = {}
    for pos in current_positions:
        token_id = pos.get("token_id")
        market_slug = pos.get("market_slug")
        side = pos.get("side")
        shares = pos.get("shares")
        
        key = f"{token_id}_{side}"
        current_state[key] = shares
        
        if key not in previous_positions:
            new_trades.append(pos)
        elif shares > previous_positions[key] * 1.05: # 5% increase
            new_trades.append(pos)

    if new_trades:
        log(f"DETECTED {len(new_trades)} NEW TRADES/ADDITIONS:")
        for trade in new_trades:
            log(f"  FOLLOW SIGNAL: {trade['market_title']} | Side: {trade['side']} | Shares: {trade['shares']}")
            # Here we could auto-execute or notify
            # For now, just log to a signals file
            with open("pbot1_signals.log", "a") as f:
                f.write(f"{datetime.now()} | SIGNAL: {trade['market_slug']} | Side: {trade['side']} | Shares: {trade['shares']}\n")
    else:
        log("No new trades detected.")

    # Save state
    with open(STATE_FILE, "w") as f:
        json.dump(current_state, f)

if __name__ == "__main__":
    monitor()
