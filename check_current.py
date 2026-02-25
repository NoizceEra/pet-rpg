import os
import requests
import json

API_KEY = os.environ.get("SIMMER_API_KEY")
BASE_URL = "https://api.simmer.markets/api/sdk"
CLOB_URL = "https://clob.polymarket.com/book"

def check_specific_arbs(market_ids):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    for mid in market_ids:
        # Get market details to get token IDs
        m_resp = requests.get(f"{BASE_URL}/markets", headers=headers, params={"ids": mid})
        m_data = m_resp.json().get("markets", [])
        if not m_data: continue
        m = m_data[0]
        question = m["question"]
        yes_token = m.get("polymarket_token_id")
        no_token = m.get("polymarket_no_token_id")
        
        print(f"Market: {question}")
        print(f"  YES Token: {yes_token}")
        print(f"  NO Token: {no_token}")
        
        # Get best asks
        def get_ask(tid):
            r = requests.get(CLOB_URL, params={"token_id": tid})
            asks = r.json().get("asks", [])
            return min(float(a["price"]) for a in asks) if asks else None

        ask_yes = get_ask(yes_token)
        ask_no = get_ask(no_token)
        
        if ask_yes is not None and ask_no is not None:
            total = ask_yes + ask_no
            print(f"  YES Ask: {ask_yes:.3f}, NO Ask: {ask_no:.3f} | Total: {total:.4f}")
            if total < 1.00:
                print(f"  💰 ARBITRAGE! Edge: {1.00 - total:.4f}")
            else:
                print(f"  No arb. Gap: {total - 1.00:.4f}")
        else:
            print(f"  Could not get asks.")

if __name__ == "__main__":
    check_specific_arbs(["b34c00a2-7e17-43f8-b2e4-e65baf67e8c3", "9f997150-f98d-4a03-9d28-238f129d3c29"])
