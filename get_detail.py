import os
import requests
import json

API_KEY = os.environ.get("SIMMER_API_KEY")
BASE_URL = "https://api.simmer.markets/api/sdk"

def get_market_detail(mid):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(f"{BASE_URL}/markets", headers=headers, params={"ids": mid})
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    get_market_detail("dc6e2688-061e-4a5a-8bca-efdd92a34230")
