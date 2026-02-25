import os
import requests
from datetime import datetime

SIMMER_API_KEY = os.getenv("SIMMER_API_KEY")

def log(msg):
    print(f"[{datetime.now()}] {msg}")

def get_active_sprint_markets():
    url = "https://api.simmer.markets/api/sdk/markets?tags=fast&status=active&limit=50"
    headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        return resp.json().get("markets", [])
    except Exception as e:
        log(f"Discovery Error: {e}")
        return []

def get_clob_price(token_id):
    url = f"https://clob.polymarket.com/midpoint?token_id={token_id}"
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if "mid" in data:
            return float(data["mid"])
        return 0
    except:
        return 0

def check_opportunities():
    markets = get_active_sprint_markets()
    log(f"Found {len(markets)} active sprint markets.")
    
    found_any = False
    for m in markets:
        yes_token = m.get("polymarket_token_id")
        no_token = m.get("polymarket_no_token_id")
        
        if not yes_token or not no_token:
            continue
            
        price_yes = get_clob_price(yes_token)
        price_no = get_clob_price(no_token)
        
        combined = price_yes + price_no
        log(f"Market: {m['question']}")
        log(f"  YES: {price_yes:.4f} | NO: {price_no:.4f} | Combined: {combined:.4f}")
        
        if 0 < combined < 1.0:
            log(f"  !!! OPPORTUNITY DETECTED !!! Edge: {1.0 - combined:.4f}")
            found_any = True
    
    if not found_any:
        log("No micro-arbitrage opportunities found in current batch.")

if __name__ == "__main__":
    check_opportunities()
