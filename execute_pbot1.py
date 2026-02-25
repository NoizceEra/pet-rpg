import os
import requests
import json
import time
import re

API_KEY = os.environ.get("SIMMER_API_KEY")
BASE_URL = "https://api.simmer.markets/api/sdk"
CLOB_URL = "https://clob.polymarket.com/book"

def get_active_markets():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {"status": "active", "limit": 100}
    response = requests.get(f"{BASE_URL}/markets", headers=headers, params=params)
    return response.json().get("markets", [])

def get_best_ask(token_id):
    try:
        response = requests.get(CLOB_URL, params={"token_id": token_id})
        data = response.json()
        asks = data.get("asks", [])
        if asks:
            # Find the minimum price among all asks
            return min(float(ask["price"]) for ask in asks)
    except Exception as e:
        print(f"Error fetching book for {token_id}: {e}")
    return None

def execute_micro_arb():
    print("Starting @PBot1 Micro-Arbitrage Execution Loop")
    markets = get_active_markets()
    
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
            delta = (m2 - m1) % 60
            if delta == 15:
                is_15m = True
        
        if not is_15m:
            continue
            
        print(f"Checking {question}...")
        
        yes_token = m.get("polymarket_token_id")
        no_token = m.get("polymarket_no_token_id")
        
        if not yes_token or not no_token:
            print("  Missing token IDs, skipping.")
            continue
            
        print(f"  Fetching YES ask for {yes_token}...")
        ask_yes = get_best_ask(yes_token)
        print(f"  Fetching NO ask for {no_token}...")
        ask_no = get_best_ask(no_token)
        
        if ask_yes is None or ask_no is None:
            print(f"  Could not get asks (YES: {ask_yes}, NO: {ask_no})")
            continue
            
        total_cost = ask_yes + ask_no
        print(f"  YES Ask: ${ask_yes:.3f}, NO Ask: ${ask_no:.3f} | Total: ${total_cost:.4f}")
        
        if total_cost < 1.00:
            edge = 1.00 - total_cost
            print(f"  💰 ARBITRAGE DETECTED! Edge: ${edge:.4f}")
            
            # Execute trade
            amount_yes = 10.0 
            amount_no = amount_yes * (ask_no / ask_yes)
            
            print(f"  Executing trades: Buy YES (${amount_yes}), Buy NO (${amount_no:.2f})")
            
            headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
            payload = {
                "trades": [
                    {"market_id": m["id"], "side": "yes", "amount": amount_yes},
                    {"market_id": m["id"], "side": "no", "amount": amount_no}
                ],
                "venue": "polymarket",
                "source": "sdk:micro-arb",
                "reasoning": f"Micro-arbitrage: YES+NO = ${total_cost:.4f}. Locked in ${edge:.4f} edge."
            }
            
            trade_resp = requests.post(f"{BASE_URL}/trades/batch", headers=headers, json=payload)
            print(f"  Trade Response: {trade_resp.status_code} - {trade_resp.text}")
            
            opportunities_found += 1
        else:
            print(f"  No arbitrage (Gap: ${total_cost - 1.00:.4f})")

    print(f"\nFinished. Found {opportunities_found} opportunities.")

if __name__ == "__main__":
    execute_micro_arb()
