import os
import requests
import json
import time
from datetime import datetime

SIMMER_API_KEY = "sk_live_67cde9c17d16218b380e3452a7dbd4d5711b4a1a3c59a58e3d838aa93248a1b0"
BASE_URL = "https://api.simmer.markets/api/sdk"

headers = {
    "Authorization": f"Bearer {SIMMER_API_KEY}",
    "Content-Type": "application/json"
}

def liquidate():
    print(f"[{datetime.now()}] Starting Liquidation of Arb Positions...")
    
    # Get positions
    resp = requests.get(f"{BASE_URL}/positions", headers=headers)
    if resp.status_code != 200:
        print(f"Failed to fetch positions: {resp.text}")
        return
        
    positions = resp.json().get("positions", [])
    print(f"Found {len(positions)} total position entries.")
    
    for p in positions:
        market_id = p['market_id']
        question = p['question']
        venue = p['venue']
        
        # Only liquidate real Polymarket positions
        if venue != "polymarket":
            continue
            
        # Sell YES shares
        shares_yes = p.get('shares_yes', 0)
        if shares_yes > 0:
            print(f"Selling {shares_yes:.4f} YES shares in {question}...")
            res = requests.post(f"{BASE_URL}/trade", headers=headers, json={
                "market_id": market_id,
                "side": "yes",
                "action": "sell",
                "shares": shares_yes,
                "venue": "polymarket",
                "reasoning": "Rotating capital into immediate, higher-frequency markets as per human instruction."
            })
            print(f"  Result: {res.status_code} {res.text}")
            time.sleep(1) # Small delay
            
        # Sell NO shares
        shares_no = p.get('shares_no', 0)
        if shares_no > 0:
            print(f"Selling {shares_no:.4f} NO shares in {question}...")
            res = requests.post(f"{BASE_URL}/trade", headers=headers, json={
                "market_id": market_id,
                "side": "no",
                "action": "sell",
                "shares": shares_no,
                "venue": "polymarket",
                "reasoning": "Rotating capital into immediate, higher-frequency markets as per human instruction."
            })
            print(f"  Result: {res.status_code} {res.text}")
            time.sleep(1)

    print(f"[{datetime.now()}] Liquidation complete.")

if __name__ == "__main__":
    liquidate()
