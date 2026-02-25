import os
import requests

SIMMER_API_KEY = os.environ.get("SIMMER_API_KEY")
url = "https://api.simmer.markets/api/sdk/user/settings"

headers = {
    "Authorization": f"Bearer {SIMMER_API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "max_trades_per_day": 500,
    "max_position_usd": 100.0,
    "auto_risk_monitor_enabled": True
}

try:
    print(f"Applying settings: {data}")
    resp = requests.patch(url, json=data, headers=headers)
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
