import os
import requests
SIMMER_API_KEY = os.getenv("SIMMER_API_KEY")
url = "https://api.simmer.markets/api/sdk/portfolio"
headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}
try:
    resp = requests.get(url, headers=headers)
    print(resp.json())
except Exception as e:
    print(f"Error: {e}")
