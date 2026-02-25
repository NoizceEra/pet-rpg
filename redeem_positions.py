import os
import requests
import json

API_KEY = "sk_live_67cde9c17d16218b380e3452a7dbd4d5711b4a1a3c59a58e3d838aa93248a1b0"
BASE_URL = "https://api.simmer.markets/api/sdk"

def redeem_all():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(f"{BASE_URL}/positions", headers=headers)
    positions = response.json().get("positions", [])
    
    for p in positions:
        if p.get("redeemable"):
            print(f"Redeeming {p['question']} ({p['redeemable_side']})...")
            payload = {
                "market_id": p["market_id"],
                "side": p["redeemable_side"]
            }
            redeem_resp = requests.post(f"{BASE_URL}/redeem", headers=headers, json=payload)
            print(f"  Status: {redeem_resp.status_code}")
            print(f"  Response: {redeem_resp.text}")

if __name__ == "__main__":
    redeem_all()
