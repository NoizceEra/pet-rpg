import os
import requests
import json
from datetime import datetime, timezone, timedelta

API_KEY = os.environ.get("SIMMER_API_KEY")
SIMMER_BASE_URL = "https://api.simmer.markets/api/sdk"
CLOB_BASE_URL = "https://clob.polymarket.com"

def get_markets(query):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    resp = requests.get(f"{SIMMER_BASE_URL}/markets?q={query}&status=active&limit=100", headers=headers)
    return resp.json().get("markets", [])

def get_order_book(token_id):
    resp = requests.get(f"{CLOB_BASE_URL}/book?token_id={token_id}")
    return resp.json()

def check_micro_arb():
    btc_markets = get_markets("Bitcoin")
    eth_markets = get_markets("Ethereum")
    all_markets = btc_markets + eth_markets
    
    now = datetime.now(timezone.utc)
    # Filter for markets resolving in the next 4 hours to catch sprints
    target_markets = []
    for m in all_markets:
        res_at = datetime.fromisoformat(m["resolves_at"].replace("Z", "+00:00"))
        if now < res_at < now + timedelta(hours=4):
            target_markets.append(m)
    
    print(f"Checking {len(target_markets)} potential sprint markets...")
    
    found_arbs = []
    
    for m in target_markets:
        print(f"Checking: {m['question']}")
        yes_token = m.get("polymarket_token_id")
        no_token = m.get("polymarket_no_token_id")
        
        if not yes_token or not no_token:
            continue
            
        try:
            yes_book = get_order_book(yes_token)
            no_book = get_order_book(no_token)
            
            yes_asks = yes_book.get("asks", [])
            no_asks = no_book.get("asks", [])
            
            if not yes_asks or not no_asks:
                continue
                
            yes_price = float(yes_asks[0]["price"])
            no_price = float(no_asks[0]["price"])
            
            combined = yes_price + no_price
            print(f"  YES: {yes_price:.4f}, NO: {no_price:.4f}, Combined: {combined:.4f}")
            
            if combined < 1.00:
                edge = 1.00 - combined
                found_arbs.append({
                    "market": m,
                    "yes_price": yes_price,
                    "no_price": no_price,
                    "combined": combined,
                    "edge": edge
                })
        except Exception as e:
            print(f"  Error checking {m['id']}: {e}")
            
    return found_arbs

if __name__ == "__main__":
    arbs = check_micro_arb()
    if arbs:
        print(f"\nFOUND {len(arbs)} MICRO-ARB OPPORTUNITIES!")
        for a in arbs:
            m = a["market"]
            print(f"Market: {m['question']}")
            print(f"  Combined Cost: ${a['combined']:.4f}")
            print(f"  Guaranteed Profit per share: ${a['edge']:.4f}")
            print(f"  ID: {m['id']}")
            print(f"  Resolves: {m['resolves_at']}")
    else:
        print("\nNo micro-arb opportunities found right now.")
