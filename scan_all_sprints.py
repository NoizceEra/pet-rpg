import os
import requests
import json
import time

API_KEY = "sk_live_67cde9c17d16218b380e3452a7dbd4d5711b4a1a3c59a58e3d838aa93248a1b0"
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
        # Check YES
        res_yes = requests.post(f"{BASE_URL}/trade", headers=HEADERS, json={
            "market_id": market_id, "side": "yes", "amount": 2.0, "dry_run": True, "venue": "polymarket"
        }).json()
        
        # Check NO
        res_no = requests.post(f"{BASE_URL}/trade", headers=HEADERS, json={
            "market_id": market_id, "side": "no", "amount": 2.0, "dry_run": True, "venue": "polymarket"
        }).json()
        
        if res_yes.get("success") and res_no.get("success"):
            price_yes = 2.0 / res_yes["shares_bought"]
            price_no = 2.0 / res_no["shares_bought"]
            total = price_yes + price_no
            return total, price_yes, price_no
    except:
        pass
    return None, None, None

queries = ["Bitcoin Up or Down", "Ethereum Up or Down"]
all_candidates = []
for q in queries:
    all_candidates.extend(get_markets(q))

print(f"Scanning {len(all_candidates)} markets...")

found_any = False
for m in all_candidates:
    question = m["question"]
    # Filter for 15m (contains a hyphen and AM/PM twice or just a duration)
    # Most 15m markets have "9:30AM-9:45AM"
    if "-" in question and ("AM" in question or "PM" in question):
        print(f"Checking: {question}")
        total, py, pn = check_arb(m["id"])
        if total is not None:
            print(f"  Cost: {total:.4f} (Y: {py:.4f}, N: {pn:.4f})")
            if total < 1.00:
                print("  !!! ARBITRAGE DETECTED !!!")
                found_any = True
                # Execute for real if edge is significant
                if total < 0.995:
                    print("  Executing trade...")
                    payload = {
                        "trades": [
                            {"market_id": m["id"], "side": "yes", "amount": 10.0},
                            {"market_id": m["id"], "side": "no", "amount": 10.0}
                        ],
                        "venue": "polymarket",
                        "source": "sdk:micro-arb",
                        "reasoning": f"Micro-arbitrage detected: combined cost ${total:.4f}"
                    }
                    exec_res = requests.post(f"{BASE_URL}/trades/batch", headers=HEADERS, json=payload).json()
                    print(f"  Execution result: {exec_res}")
        time.sleep(0.1)

if not found_any:
    print("No arbitrage found in any 15-minute sprint markets.")
