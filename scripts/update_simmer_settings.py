import os
import requests
import json

api_key = os.environ.get("SIMMER_API_KEY")
if not api_key:
    print("Error: SIMMER_API_KEY not found in environment")
    exit(1)

url = "https://api.simmer.markets/api/sdk/user/settings"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Payload inferred from user's failed command
payload = {
    "max_trades_per_day": 500,
    "max_position_usd": 500.0,
    "auto_risk_monitor_enabled": True,
    "trading_paused": False
}

print(f"Updating Simmer settings with payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.patch(url, headers=headers, json=payload)
    response.raise_for_status()
    print("\nSuccess! New settings:")
    print(json.dumps(response.json(), indent=2))
except requests.exceptions.RequestException as e:
    print(f"\nError updating settings: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response: {e.response.text}")
