import os
import requests
import json
import time

API_KEY = os.environ.get("SIMMER_API_KEY")
BASE_URL = "https://api.simmer.markets/api/sdk"
CLOB_URL = "https://clob.polymarket.com/book"

def scan_books():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {"status": "active", "limit": 100, "q": "Up or Down"}
    response = requests.get(f"{BASE_URL}/markets", headers=headers, params=params)
    markets = response.json().get("markets", [])
    
    for m in markets:
        question = m["question"]
        yes_token = m.get("polymarket_token_id")
        no_token = m.get("polymarket_no_token_id")
        
        if not yes_token or not no_token: continue
        
        def get_ask(tid):
            try:
                r = requests.get(CLOB_URL, params={"token_id": tid})
                if r.status_code == 200:
                    asks = r.json().get("asks", [])
                    return min(float(a["price"]) for a in asks) if asks else "No Asks"
                else:
                    return f"Error {r.status_code}"
            except Exception as e:
                return str(e)

        ask_yes = get_ask(yes_token)
        ask_no = get_ask(no_token)
        
        if ask_yes != "Error 404" and ask_no != "Error 404":
            print(f"Market: {question}")
            print(f"  YES: {ask_yes}, NO: {ask_no}")
            if isinstance(ask_yes, float) and isinstance(ask_no, float):
                total = ask_yes + ask_no
                print(f"  Total: {total:.4f}")
                if total < 1.00:
                    print("  💰 ARB!")

if __name__ == "__main__":
    scan_books()
