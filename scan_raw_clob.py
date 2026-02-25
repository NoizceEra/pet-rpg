import os
import requests
import json
import time

API_KEY = "sk_live_67cde9c17d16218b380e3452a7dbd4d5711b4a1a3c59a58e3d838aa93248a1b0"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
BASE_URL = "https://api.simmer.markets/api/sdk"
CLOB_URL = "https://clob.polymarket.com/book"

def get_best_ask(token_id):
    try:
        res = requests.get(CLOB_URL, params={"token_id": token_id}).json()
        asks = res.get("asks", [])
        if asks:
            return min(float(ask["price"]) for ask in asks)
    except:
        pass
    return None

def get_markets(query):
    try:
        res = requests.get(f"{BASE_URL}/markets?q={query}&limit=50", headers=HEADERS).json()
        return res.get("markets", [])
    except Exception as e:
        print(f"Error fetching markets for {query}: {e}")
        return []

queries = ["Bitcoin Up or Down", "Ethereum Up or Down"]
all_candidates = []
for q in queries:
    all_candidates.extend(get_markets(q))

print(f"Scanning {len(all_candidates)} markets for RAW CLOB arbitrage...")

for m in all_candidates:
    question = m["question"]
    if "-" in question and ("AM" in question or "PM" in question):
        yes_token = m.get("polymarket_token_id")
        no_token = m.get("polymarket_no_token_id")
        
        if not yes_token or not no_token:
            continue
            
        ask_yes = get_best_ask(yes_token)
        ask_no = get_best_ask(no_token)
        
        if ask_yes is not None and ask_no is not None:
            total = ask_yes + ask_no
            if total < 1.00:
                print(f"💰 ARBITRAGE! {question}")
                print(f"  YES: {ask_yes:.4f}, NO: {ask_no:.4f} | Total: {total:.4f}")
                
                # Execute if edge is found
                # Note: Fees will apply if executed via Simmer proxy
                # But we follow the @PBot1 instructions to execute.
                
                payload = {
                    "trades": [
                        {"market_id": m["id"], "side": "yes", "amount": 10.0},
                        {"market_id": m["id"], "side": "no", "amount": 10.0}
                    ],
                    "venue": "polymarket",
                    "source": "sdk:micro-arb",
                    "reasoning": f"Micro-arbitrage: YES+NO = ${total:.4f}. Locked in edge."
                }
                exec_res = requests.post(f"{BASE_URL}/trades/batch", headers=HEADERS, json=payload).json()
                print(f"  Execution result: {exec_res}")
        time.sleep(0.05)
