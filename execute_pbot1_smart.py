import os
import requests
import json
import time
import re
from datetime import datetime, timedelta

API_KEY = os.environ.get("SIMMER_API_KEY")
BASE_URL = "https://api.simmer.markets/api/sdk"
CLOB_URL = "https://clob.polymarket.com/book"

def get_active_markets():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {"status": "active", "limit": 100, "sort": "date"}
    response = requests.get(f"{BASE_URL}/markets", headers=headers, params=params)
    return response.json().get("markets", [])

def get_best_ask(token_id):
    try:
        response = requests.get(CLOB_URL, params={"token_id": token_id})
        data = response.json()
        asks = data.get("asks", [])
        if asks:
            return min(float(ask["price"]) for ask in asks)
    except Exception as e:
        pass
    return None

def get_balance():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(f"{BASE_URL}/agents/me", headers=headers)
    return response.json().get("balance", 0)

def execute_micro_arb():
    print(f"[{datetime.now().isoformat()}] Starting @PBot1 Micro-Arbitrage Execution")
    
    balance = get_balance()
    print(f"Current Balance: {balance:.2f}")
    
    # Smart sizing: 0.5% of balance, capped at $100
    trade_size = min(balance * 0.005, 100.0)
    if trade_size < 5.0: # Minimum $5 per side for meaningful arb
        trade_size = 5.0
    print(f"Target Trade Size: ${trade_size:.2f}")

    markets = get_active_markets()
    print(f"Fetched {len(markets)} active markets.")
    opportunities_found = 0
    
    now_utc = datetime.utcnow()
    
    for m in markets:
        question = m["question"]
        if ("Bitcoin Up or Down" not in question and "Ethereum Up or Down" not in question):
            continue
            
        # Parse time window and duration
        # Format: "Bitcoin Up or Down - February 16, 4:00AM-4:15AM ET"
        match = re.search(r'(\d+):(\d+)(AM|PM)\s*-\s*(\d+):(\d+)(AM|PM)', question)
        if not match:
            continue
            
        h1, m1, p1, h2, m2, p2 = match.groups()
        
        # Simple duration check
        start_min = int(h1) * 60 + int(m1)
        if p1 == "PM" and h1 != "12": start_min += 12 * 60
        if p1 == "AM" and h1 == "12": start_min -= 12 * 60
        
        end_min = int(h2) * 60 + int(m2)
        if p2 == "PM" and h2 != "12": end_min += 12 * 60
        if p2 == "AM" and h2 == "12": end_min -= 12 * 60
        
        duration = (end_min - start_min) % (24 * 60)
        
        if duration != 15:
            # print(f"Skipping {question} (Duration: {duration}m)")
            continue
            
        # Time check: Skip if resolution is in the past
        res_at = m.get("resolves_at")
        if res_at:
            try:
                # Handle "Z" as UTC
                res_at_clean = res_at.replace("Z", "+0000")
                res_dt = datetime.strptime(res_at_clean, "%Y-%m-%d %H:%M:%S%z").replace(tzinfo=None)
                if res_dt < now_utc:
                    continue
            except Exception as e:
                # print(f"Error parsing time for {question}: {e}")
                pass

        print(f"Checking 15m market: {question}")
        
        yes_token = m.get("polymarket_token_id")
        no_token = m.get("polymarket_no_token_id")
        
        if not yes_token or not no_token:
            continue
            
        ask_yes = get_best_ask(yes_token)
        ask_no = get_best_ask(no_token)
        
        if ask_yes is None or ask_no is None:
            continue
            
        total_cost = ask_yes + ask_no
        print(f"  YES: ${ask_yes:.3f}, NO: ${ask_no:.3f} | Total: ${total_cost:.4f}")
        
        if total_cost < 1.00:
            edge = 1.00 - total_cost
            print(f"  💰 ARBITRAGE! Edge: ${edge:.4f}")
            
            # Smart sizing: buy both sides such that we spend trade_size total
            # cost = (shares * ask_yes) + (shares * ask_no) = shares * total_cost
            # shares = trade_size / total_cost
            shares = trade_size / total_cost
            amount_yes = shares * ask_yes
            amount_no = shares * ask_no
            
            print(f"  Executing: Buy YES (${amount_yes:.2f}), Buy NO (${amount_no:.2f})")
            
            headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
            payload = {
                "trades": [
                    {"market_id": m["id"], "side": "yes", "amount": amount_yes},
                    {"market_id": m["id"], "side": "no", "amount": amount_no}
                ],
                "venue": "polymarket",
                "source": "sdk:micro-arb",
                "reasoning": f"@PBot1 Micro-Arb strategy: Combined cost ${total_cost:.4f} < $1.00. Edge: ${edge:.4f}. Smart sizing ${trade_size:.2f} total."
            }
            
            try:
                resp = requests.post(f"{BASE_URL}/trades/batch", headers=headers, json=payload)
                print(f"  Response: {resp.status_code} - {resp.text}")
                opportunities_found += 1
            except Exception as e:
                print(f"  Trade Error: {e}")
        else:
            print(f"  Gap: ${total_cost - 1.00:.4f}")

    print(f"Finished. Captured {opportunities_found} opportunities.")

if __name__ == "__main__":
    execute_micro_arb()
