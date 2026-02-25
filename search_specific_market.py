import os
import requests
import json

API_KEY = os.environ.get("SIMMER_API_KEY")
BASE_URL = "https://api.simmer.markets/api/sdk"

headers = {"Authorization": f"Bearer {API_KEY}"}
params = {"status": "active", "q": "5:30AM"}
markets = requests.get(f"{BASE_URL}/markets", headers=headers, params=params).json().get("markets", [])

for m in markets:
    print(m["question"])
