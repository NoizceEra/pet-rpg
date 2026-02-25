import os
import requests
import json
import time
from datetime import datetime

SIMMER_API_KEY = "sk_live_67cde9c17d16218b380e3452a7dbd4d5711b4a1a3c59a58e3d838aa93248a1b0"
BASE_URL = "https://api.simmer.markets/api/sdk"

headers = {
    "Authorization": f"Bearer {SIMMER_API_KEY}",
    "Content-Type": "application/json"
}

def get_ask(token_id):
    if not token_id: return 1.0
    url = f"https://clob.polymarket.com/price?token_id={token_id}&side=buy"
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if "price" in data:
            return float(data["price"])
    except:
        pass
    return 1.0

def hunt():
    print(f"[{datetime.now()}] Hunting TODAY Arbs...")
    
    # Get active sprint markets
    resp = requests.get(f"{BASE_URL}/markets?tags=fast&status=active&limit=100", headers=headers)
    markets = resp.json().get("markets", [])
    
    now = datetime.utcnow()
    found_count = 0
    
    for m in markets:
        q = m['question']
        # Only look at today's markets (Feb 16)
        if "February 16" not in q:
            continue
            
        market_id = m['id']
        token_yes = m.get('polymarket_token_id')
        token_no = m.get('polymarket_no_token_id')
        
        if not token_yes or not token_no:
            continue
            
        ask_yes = get_ask(token_yes)
        ask_no = get_ask(token_no)
        combined = ask_yes + ask_no
        
        if ask_yes < 1.0 and ask_no < 1.0:
            print(f"Market: {q}")
            print(f"  YES Ask: {ask_yes:.4f} | NO Ask: {ask_no:.4f} | Combined: {combined:.4f}")
            
            if combined < 1.0:
                edge = 1.0 - combined
                print(f"  !!! ARB FOUND !!! Edge: {edge:.4f}")
                
                # Minimum trade is $5 per side ($10 total)
                # We have $7.82 remaining. We can't trade this yet if it requires $10.
                # But we should check if we can trade smaller amounts?
                # Usually Simmer/Polymarket has a $5 minimum.
                
                found_count += 1
                
    print(f"[{datetime.now()}] Hunt complete. Found {found_count} opportunities.")

if __name__ == "__main__":
    hunt()
