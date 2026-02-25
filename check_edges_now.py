import os
import requests
import json

API_KEY = os.environ.get("SIMMER_API_KEY")
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

headers = {"Authorization": f"Bearer {API_KEY}"}
params = {"status": "active", "limit": 100}
markets = requests.get(f"{BASE_URL}/markets", headers=headers, params=params).json().get("markets", [])

print(f"Current Time: {requests.get(f'{BASE_URL}/health').headers.get('Date')}")
print("Scanning for Micro-Arb edges...")

for m in markets:
    q = m["question"]
    if "Bitcoin Up or Down" in q or "Ethereum Up or Down" in q:
        p_yes = m.get("current_probability")
        print(f"{q}: YES={p_yes}")
