import os
import requests
import json
import time
import re

API_KEY = "sk_live_67cde9c17d16218b380e3452a7dbd4d5711b4a1a3c59a58e3d838aa93248a1b0"
BASE_URL = "https://api.simmer.markets/api/sdk"
CLOB_URL = "https://clob.polymarket.com/book"

def get_active_markets():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {"status": "active", "limit": 50}
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
        print(f"Error fetching book for {token_id}: {e}")
    return None

def execute_micro_arb():
    print("Scanning for BTC/ETH 15m Sprint Arbs...")
    markets = get_active_markets()
    print(f"Retrieved {len(markets)} active markets.")
    
    opportunities_found = 0
    
    for m in markets:
        question = m["question"]
        
        # Filter for BTC/ETH Up or Down markets
        if ("Bitcoin Up or Down" not in question and "Ethereum Up or Down" not in question):
            continue
            
        # Filter for 15-minute windows
        is_15m = False
        time_match = re.search(r'(\d+):(\d+)(?:AM|PM)?\s*-\s*(\d+):(\d+)(?:AM|PM)?', question)
        if time_match:
            h1, m1, h2, m2 = map(int, time_match.groups())
            # Simple check for 15 min gap
            if (m2 - m1) % 60 == 15:
                is_15m = True
        
        if not is_15m:
            continue
            
        print(f"Analyzing: {question}")
        
        yes_token = m.get("polymarket_token_id")
        no_token = m.get("polymarket_no_token_id")
        
        if not yes_token or not no_token:
            continue
            
        ask_yes = get_best_ask(yes_token)
        ask_no = get_best_ask(no_token)
        
        if ask_yes is None or ask_no is None:
            continue
            
        total_cost = ask_yes + ask_no
        print(f"  YES: {ask_yes:.3f} | NO: {ask_no:.3f} | Sum: {total_cost:.4f}")
        
        if total_cost < 1.00:
            edge = 1.00 - total_cost
            print(f"  ARB FOUND! Edge: ${edge:.4f}")
            
            # Execute trade
            amount_yes = 5.0 
            amount_no = amount_yes * (ask_no / ask_yes)
            
            payload = {
                "trades": [
                    {"market_id": m["id"], "side": "yes", "amount": amount_yes},
                    {"market_id": m["id"], "side": "no", "amount": amount_no}
                ],
                "venue": "polymarket",
                "source": "sdk:micro-arb",
                "reasoning": f"Micro-arbitrage: YES+NO = ${total_cost:.4f}. Locked in ${edge:.4f} edge."
            }
            
            headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
            trade_resp = requests.post(f"{BASE_URL}/trades/batch", headers=headers, json=payload)
            print(f"  Trade Status: {trade_resp.status_code}")
            
            opportunities_found += 1

    print(f"\nScan complete. Opportunities found: {opportunities_found}")

if __name__ == "__main__":
    execute_micro_arb()
