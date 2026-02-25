import os
import requests
import json

API_KEY = "sk_live_5aad9ec4285ca9686cc7df046d5b5cf1f2684310c37c3e71983e9980baa1d0b7"
BASE_URL = "https://api.simmer.markets/api/sdk"

def check_portfolio():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(f"{BASE_URL}/portfolio", headers=headers)
    print("Portfolio:", json.dumps(response.json(), indent=2))
    
    response = requests.get(f"{BASE_URL}/positions", headers=headers)
    print("Positions:", json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    check_portfolio()
