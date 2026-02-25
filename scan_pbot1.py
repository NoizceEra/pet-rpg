
import os
import requests
import json
import time

API_KEY = os.environ.get("SIMMER_API_KEY")
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
BASE_URL = "https://api.simmer.markets/api/sdk"

def get_markets(query):
    try:
        res = requests.get(f"{BASE_URL}/markets?q={query}&limit=50", headers=HEADERS).json()
        return res.get("markets", [])
    except Exception as e:
        print(f"Error fetching markets for {query}: {e}")
        return []

def check_arb(market_id):
    try:
        # Dry run YES
        yes_res = requests.post(f"{BASE_URL}/trade", headers=HEADERS, json={
            "market_id": market_id, "side": "yes", "amount": 1.0, "dry_run": True, "venue": "polymarket"
        }).json()
        
        # Dry run NO
        no_res = requests.post(f"{BASE_URL}/trade", headers=HEADERS, json={
            "market_id": market_id, "side": "no", "amount": 1.0, "dry_run": True, "venue": "polymarket"
        }).json()
        
        if not yes_res.get("success") or not no_res.get("success"):
            return None
            
        # Actual cost per share including fees/slippage
        price_yes = 1.0 / yes_res["shares_bought"]
        price_no = 1.0 / no_res["shares_bought"]
        total_cost = price_yes + price_no
        
        return {
            "id": market_id,
            "total_cost": total_cost,
            "price_yes": price_yes,
            "price_no": price_no,
            "fee_bps": yes_res.get("fee_rate_bps", 0)
        }
    except:
        return None

# Find BTC and ETH sprint markets
btc_markets = get_markets("Bitcoin Up or Down")
eth_markets = get_markets("Ethereum Up or Down")
all_markets = btc_markets + eth_markets

print(f"Found {len(all_markets)} candidate markets.")

arbs = []
for m in all_markets:
    # Filter for 15-min or 5-min intervals (e.g., "5:00AM-5:15AM" or "5:00AM-5:05AM")
    # Actually, the strategy just says 15-minute BTC and ETH sprint markets.
    # Titles like "Bitcoin Up or Down - February 16, 5:00AM-5:15AM ET"
    question = m["question"]
    if "-" in question and "AM" in question:
        print(f"Checking: {question}")
        res = check_arb(m["id"])
        if res:
            res["question"] = question
            print(f"  Cost: {res['total_cost']:.4f}")
            if res["total_cost"] < 1.00:
                print(f"  !!! ARB FOUND !!!")
                arbs.append(res)
        time.sleep(0.5)

if arbs:
    print("\n--- ARBITRAGE OPPORTUNITIES ---")
    print(json.dumps(arbs, indent=2))
else:
    print("\nNo micro-arbitrage opportunities found currently.")
