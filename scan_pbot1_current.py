import os
import requests
import json
from datetime import datetime

API_KEY = os.environ.get("SIMMER_API_KEY")
BASE_URL = "https://api.simmer.markets/api/sdk"

def scan():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {"q": "Up or Down", "status": "active", "limit": 20}
    try:
        print(f"[{datetime.now().isoformat()}] Fetching sprint markets...")
        response = requests.get(f"{BASE_URL}/markets", headers=headers, params=params, timeout=10)
        markets = response.json().get("markets", [])
        print(f"Found {len(markets)} candidate markets.")
        
        results = []
        for m in markets:
            if "15-minute" in m.get("tags", []) or "15m" in m.get("tags", []):
                results.append(m)
            elif "15m" in m["question"] or "15-minute" in m["question"]:
                results.append(m)
            # 15m markets usually have a time range in the name
            elif "-" in m["question"] and ":" in m["question"]:
                 results.append(m)
                 
        print(f"Filtered to {len(results)} potential 15m markets.")
        
        for m in results:
            print(f"Market: {m['question']}")
            print(f"  YES Price: {m['current_probability']}")
            # We need the NO price, which isn't in the market summary usually, 
            # but we can check the CLOB if we have the token ID.
            
            yes_token = m.get("polymarket_token_id")
            no_token = m.get("polymarket_no_token_id")
            
            if yes_token and no_token:
                print(f"  YES Token: {yes_token}")
                print(f"  NO Token: {no_token}")
                
                # Check CLOB for best asks
                try:
                    yes_resp = requests.get(f"https://clob.polymarket.com/book?token_id={yes_token}", timeout=5)
                    no_resp = requests.get(f"https://clob.polymarket.com/book?token_id={no_token}", timeout=5)
                    
                    yes_asks = yes_resp.json().get("asks", [])
                    no_asks = no_resp.json().get("asks", [])
                    
                    if yes_asks and no_asks:
                        best_yes = min(float(a["price"]) for a in yes_asks)
                        best_no = min(float(a["price"]) for a in no_asks)
                        total = best_yes + best_no
                        print(f"  Best YES Ask: ${best_yes:.3f}, Best NO Ask: ${best_no:.3f} | Total: ${total:.4f}")
                        
                        if total < 1.00:
                            print(f"  💰 ARBITRAGE FOUND! Edge: ${1.00 - total:.4f}")
                    else:
                        print("  One or both sides lack asks on CLOB.")
                except Exception as e:
                    print(f"  Error checking CLOB: {e}")
            else:
                print("  Missing token IDs for arbitrage check.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    scan()
