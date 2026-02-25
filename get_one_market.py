import os
import requests
import json

API_KEY = "sk_live_67cde9c17d16218b380e3452a7dbd4d5711b4a1a3c59a58e3d838aa93248a1b0"
BASE_URL = "https://api.simmer.markets/api/sdk"

def get_market_details(market_id):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(f"{BASE_URL}/markets", headers=headers, params={"ids": market_id})
    return response.json().get("markets", [])[0]

if __name__ == "__main__":
    m = get_market_details("75d937bd-ac4f-4586-99ba-1b7dd8f53d43")
    print(json.dumps(m, indent=2))
