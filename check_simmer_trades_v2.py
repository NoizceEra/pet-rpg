import os
import requests
import json

API_KEY = "sk_live_67cde9c17d16218b380e3452a7dbd4d5711b4a1a3c59a58e3d838aa93248a1b0"
BASE_URL = "https://api.simmer.markets/api/sdk"

def check_trades():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(f"{BASE_URL}/trades", headers=headers, params={"limit": 20})
    data = response.json()
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    check_trades()
