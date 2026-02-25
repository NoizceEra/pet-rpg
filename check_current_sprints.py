import os
import requests
import json

API_KEY = "sk_live_67cde9c17d16218b380e3452a7dbd4d5711b4a1a3c59a58e3d838aa93248a1b0"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
BASE_URL = "https://api.simmer.markets/api/sdk"

markets = [
    {"id": "a8a3aaa5-e1fa-42a0-9b4f-c20affda239a", "name": "ETH 10:15AM-10:30AM"},
    {"id": "2b2ea15d-62fd-4166-97ee-e3c898c0aa77", "name": "BTC 10:15AM-10:30AM"}
]

for m in markets:
    print(f"Checking {m['name']} ({m['id']})...")
    try:
        # Check YES
        res_yes = requests.post(f"{BASE_URL}/trade", headers=HEADERS, json={
            "market_id": m["id"], "side": "yes", "amount": 5.0, "dry_run": True, "venue": "polymarket"
        }).json()
        
        # Check NO
        res_no = requests.post(f"{BASE_URL}/trade", headers=HEADERS, json={
            "market_id": m["id"], "side": "no", "amount": 5.0, "dry_run": True, "venue": "polymarket"
        }).json()
        
        if res_yes.get("success") and res_no.get("success"):
            price_yes = 5.0 / res_yes["shares_bought"]
            price_no = 5.0 / res_no["shares_bought"]
            total = price_yes + price_no
            print(f"  YES Price: {price_yes:.4f}")
            print(f"  NO Price:  {price_no:.4f}")
            print(f"  Total:     {total:.4f}")
            if total < 1.00:
                print("  !!! ARBITRAGE !!!")
            else:
                print("  No arbitrage.")
        else:
            print(f"  Failed: YES={res_yes.get('success')}, NO={res_no.get('success')}")
            print(f"  Error YES: {res_yes.get('detail')}")
            print(f"  Error NO: {res_no.get('detail')}")
    except Exception as e:
        print(f"  Error: {e}")
