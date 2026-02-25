import os
import requests
import json

API_KEY = "sk_live_67cde9c17d16218b380e3452a7dbd4d5711b4a1a3c59a58e3d838aa93248a1b0"
BASE_URL = "https://api.simmer.markets/api/sdk"
CLOB_URL = "https://clob.polymarket.com/book"

def get_best_ask(token_id):
    try:
        response = requests.get(CLOB_URL, params={"token_id": token_id})
        data = response.json()
        asks = data.get("asks", [])
        if asks:
            return min(float(ask["price"]) for ask in asks)
    except: pass
    return None

def check():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    # Search for BTC and ETH sprint markets resolving soon
    params = {"status": "active", "limit": 20, "q": "Up or Down"}
    markets = requests.get(f"{BASE_URL}/markets", headers=headers, params=params).json().get("markets", [])
    
    for m in markets:
        print(f"Market: {m['question']}")
        y_id = m.get('polymarket_token_id')
        n_id = m.get('polymarket_no_token_id')
        if y_id and n_id:
            y_ask = get_best_ask(y_id)
            n_ask = get_best_ask(n_id)
            if y_ask and n_ask:
                total = y_ask + n_ask
                print(f"  YES: {y_ask:.3f}, NO: {n_ask:.3f} | Total: {total:.4f}")
                if total < 1.0:
                    print(f"  💰 EDGE FOUND: {1.0 - total:.4f}")
            else:
                print("  Missing liquidity on one side")
        else:
            print("  Missing token IDs")

if __name__ == "__main__":
    check()
