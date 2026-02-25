import os
import requests
import json

API_KEY = os.environ.get("SIMMER_API_KEY")
BASE_URL = "https://api.simmer.markets/api/sdk"

def list_recent():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {"status": "active", "limit": 20, "sort": "date"}
    response = requests.get(f"{BASE_URL}/markets", headers=headers, params=params)
    markets = response.json().get("markets", [])
    for m in markets:
        print(f"ID: {m['id']} | Question: {m['question']}")

if __name__ == "__main__":
    list_recent()
