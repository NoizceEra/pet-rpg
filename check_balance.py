import os
import requests

SIMMER_API_KEY = os.getenv("SIMMER_API_KEY")
headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}

resp = requests.get('https://api.simmer.markets/api/sdk/portfolio', headers=headers)
print(resp.json())
