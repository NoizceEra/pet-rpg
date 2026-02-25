import os
import requests
import json
import re
from datetime import datetime, timezone, timedelta

API_KEY = "sk_live_67cde9c17d16218b380e3452a7dbd4d5711b4a1a3c59a58e3d838aa93248a1b0"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
BASE_URL = "https://api.simmer.markets/api/sdk"

def get_active_markets():
    # Use briefing to get all relevant data in one call
    response = requests.get(f"{BASE_URL}/briefing", headers=HEADERS)
    briefing = response.json()
    # Also get some search results just in case
    search_resp = requests.get(f"{BASE_URL}/markets?q=Up%20or%20Down&status=active&limit=100", headers=HEADERS)
    search_markets = search_resp.json().get("markets", [])
    
    # Combine
    all_markets = search_markets
    seen = {m["id"] for m in all_markets}
    for m in briefing.get("opportunities", {}).get("new_markets", []):
        if m["id"] not in seen:
            all_markets.append(m)
            seen.add(m["id"])
            
    return all_markets

def check_arb(market_id, amount=10.0):
    try:
        # Check YES
        res_yes = requests.post(f"{BASE_URL}/trade", headers=HEADERS, json={
            "market_id": market_id, "side": "yes", "amount": amount, "dry_run": True, "venue": "polymarket"
        }).json()
        
        # Check NO
        res_no = requests.post(f"{BASE_URL}/trade", headers=HEADERS, json={
            "market_id": market_id, "side": "no", "amount": amount, "dry_run": True, "venue": "polymarket"
        }).json()
        
        if res_yes.get("shares_bought") and res_no.get("shares_bought"):
            # Price including fees and slippage
            price_yes = amount / res_yes["shares_bought"]
            price_no = amount / res_no["shares_bought"]
            total = price_yes + price_no
            return price_yes, price_no, total, res_yes.get("fee_rate_bps", 0)
    except Exception:
        pass
    return None, None, None, None

def main():
    print(f"[{datetime.now().isoformat()}] Starting @PBot1 Autonomous Scan")
    markets = get_active_markets()
    print(f"Total active candidates: {len(markets)}")
    
    now = datetime.now(timezone.utc)
    found_any = False
    captured = []
    
    for m in markets:
        question = m["question"]
        if "Bitcoin" not in question and "Ethereum" not in question:
            continue
            
        # Match 15m pattern: "8:30AM-8:45AM"
        match = re.search(r'(\d+):(\d+)(AM|PM)\s*-\s*(\d+):(\d+)(AM|PM)', question)
        if not match:
            continue
            
        # Calculate duration
        h1, m1, p1, h2, m2, p2 = match.groups()
        start_min = (int(h1) % 12 + (12 if p1 == "PM" else 0)) * 60 + int(m1)
        end_min = (int(h2) % 12 + (12 if p2 == "PM" else 0)) * 60 + int(m2)
        duration = (end_min - start_min) % (24 * 60)
        
        if duration != 15:
            continue
            
        # Check if expired
        res_at_str = m.get("resolves_at")
        if res_at_str:
            res_at = datetime.fromisoformat(res_at_str.replace("Z", "+00:00"))
            if res_at < now + timedelta(minutes=1):
                continue

        print(f"Checking 15m Market: {question} (ID: {m['id']})")
        found_any = True
        
        p_yes, p_no, total, fee = check_arb(m["id"])
        if p_yes:
            print(f"  Prices: YES {p_yes:.4f} | NO {p_no:.4f} | Total {total:.4f} (Fee: {fee} bps)")
            if total < 0.999: # Allow for tiny rounding
                edge = 1.0 - total
                print(f"  💰 ARBITRAGE! Edge: {edge:.4f}")
                
                # EXECUTE TRADE
                # Sizing: $10 total as a start
                payload = {
                    "trades": [
                        {"market_id": m["id"], "side": "yes", "amount": 5.0},
                        {"market_id": m["id"], "side": "no", "amount": 5.0}
                    ],
                    "venue": "polymarket",
                    "source": "sdk:micro-arb",
                    "reasoning": f"@PBot1 Micro-Arb: Combined cost {total:.4f} < 1.0. Edge: {edge:.4f}."
                }
                # Uncomment to go live
                # resp = requests.post(f"{BASE_URL}/trades/batch", headers=HEADERS, json=payload)
                # print(f"  Execution Response: {resp.status_code}")
                # captured.append(f"{question}: Edge {edge:.4f}")
            else:
                print(f"  No Edge.")
        else:
            print("  Prices unavailable.")

    if not found_any:
        print("No 15-minute BTC/ETH sprint markets found.")
    
    if captured:
        print("\nSUMMARY OF CAPTURES:")
        for c in captured:
            print(f" - {c}")
    else:
        print("\nNo arbs captured in this cycle.")

if __name__ == "__main__":
    main()
