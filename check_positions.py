import os
import requests
import json

SIMMER_API_KEY = os.getenv("SIMMER_API_KEY")
headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}

resp = requests.get('https://api.simmer.markets/api/sdk/positions', headers=headers)
print(json.dumps(resp.json(), indent=2))
