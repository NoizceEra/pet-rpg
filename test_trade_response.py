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
    params = {"status": "active", "limit": 10}
    response = requests.get(f"{BASE_URL}/markets", headers=headers, params=params)
    return response.json().get("markets", [])

def execute_single_arb_test():
    markets = get_active_markets()
    for m in markets:
        if "Bitcoin Up or Down" in m["question"]:
            print(f"Testing with {m['question']}")
            payload = {
                "trades": [
                    {"market_id": m["id"], "side": "yes", "amount": 1.0},
                    {"market_id": m["id"], "side": "no", "amount": 1.0}
                ],
                "venue": "polymarket",
                "source": "sdk:micro-arb-test",
                "reasoning": "Test with small amount due to low balance."
            }
            headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
            trade_resp = requests.post(f"{BASE_URL}/trades/batch", headers=headers, json=payload)
            print(f"Status: {trade_resp.status_code}")
            print(f"Response: {trade_resp.text}")
            break

if __name__ == "__main__":
    execute_single_arb_test()
