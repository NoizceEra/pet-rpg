import os
import requests
import json
import re
from datetime import datetime, timezone, timedelta

API_KEY = "sk_live_67cde9c17d16218b380e3452a7dbd4d5711b4a1a3c59a58e3d838aa93248a1b0"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
BASE_URL = "https://api.simmer.markets/api/sdk"

def get_active_markets():
    params = {"status": "active", "limit": 100, "q": "Up or Down"}
    response = requests.get(f"{BASE_URL}/markets", headers=HEADERS, params=params)
    return response.json().get("markets", [])

def check_arb(market_id, amount=10.0):
    try:
        res_yes = requests.post(f"{BASE_URL}/trade", headers=HEADERS, json={
            "market_id": market_id, "side": "yes", "amount": amount, "dry_run": True, "venue": "polymarket"
        }).json()
        res_no = requests.post(f"{BASE_URL}/trade", headers=HEADERS, json={
            "market_id": market_id, "side": "no", "amount": amount, "dry_run": True, "venue": "polymarket"
        }).json()
        
        if res_yes.get("shares_bought") and res_no.get("shares_bought"):
            p_yes = amount / res_yes["shares_bought"]
            p_no = amount / res_no["shares_bought"]
            return p_yes, p_no, p_yes + p_no, res_yes.get("fee_rate_bps", 0)
    except: pass
    return None, None, None, None

def main():
    print(f"[{datetime.now().isoformat()}] @PBot1 Strategy Execution")
    markets = get_active_markets()
    now = datetime.now(timezone.utc)
    
    found_any = False
    for m in markets:
        q = m["question"]
        if not ("Bitcoin" in q or "Ethereum" in q): continue
        if not re.search(r'\d+:\d+(AM|PM)\s*-\s*\d+:\d+(AM|PM)', q): continue
        
        # Duration check
        match = re.search(r'(\d+):(\d+)(AM|PM)\s*-\s*(\d+):(\d+)(AM|PM)', q)
        h1, m1, p1, h2, m2, p2 = match.groups()
        start = (int(h1)%12 + (12 if p1=="PM" else 0))*60 + int(m1)
        end = (int(h2)%12 + (12 if p2=="PM" else 0))*60 + int(m2)
        if (end-start)%1440 != 15: continue
        
        res_at = datetime.fromisoformat(m["resolves_at"].replace("Z", "+00:00"))
        if res_at < now: continue
        
        print(f"Target: {q}")
        p_yes, p_no, total, fee = check_arb(m["id"])
        if p_yes:
            print(f"  YES: {p_yes:.4f}, NO: {p_no:.4f}, Total: {total:.4f} (Fee: {fee})")
            if total < 0.9995:
                edge = 1.0 - total
                print(f"  💰 ARBITRAGE! Capture: Buy YES/NO. Edge: {edge:.4f}")
                # Real execution
                payload = {
                    "trades": [{"market_id": m["id"], "side": "yes", "amount": 10.0}, {"market_id": m["id"], "side": "no", "amount": 10.0}],
                    "venue": "polymarket", "source": "sdk:micro-arb",
                    "reasoning": f"@PBot1 Micro-Arb Capture: Total cost {total:.4f} < 1.0. Edge: {edge:.4f}."
                }
                resp = requests.post(f"{BASE_URL}/trades/batch", headers=HEADERS, json=payload)
                print(f"  Execution: {resp.status_code} {resp.text}")
                found_any = True
            else:
                print(f"  No Edge.")
        else:
            print("  Prices not available.")

    if not found_any:
        print("No arbs found in current 15m windows.")

if __name__ == "__main__":
    main()
