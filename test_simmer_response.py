import os
import requests
import json

API_KEY = "sk_live_67cde9c17d16218b380e3452a7dbd4d5711b4a1a3c59a58e3d838aa93248a1b0"
BASE_URL = "https://api.simmer.markets/api/sdk"

def test():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {"q": "Up or Down", "limit": 1}
    response = requests.get(f"{BASE_URL}/markets", headers=headers, params=params)
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test()
