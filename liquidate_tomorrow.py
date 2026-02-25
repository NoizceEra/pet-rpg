import os
import requests
import json

API_KEY = "sk_live_67cde9c17d16218b380e3452a7dbd4d5711b4a1a3c59a58e3d838aa93248a1b0"
BASE_URL = "https://api.simmer.markets/api/sdk"

def get_positions():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(f"{BASE_URL}/positions", headers=headers)
    return response.json()

def liquidate_position(market_id, side, shares, reasoning):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "market_id": market_id,
        "side": side,
        "action": "sell",
        "shares": shares,
        "venue": "polymarket",
        "reasoning": reasoning
    }
    response = requests.post(f"{BASE_URL}/trade", headers=headers, json=payload)
    return response.json()

def main():
    data = get_positions()
    if isinstance(data, dict):
        positions = data.get('positions', [])
    else:
        positions = data
    print(f"Found {len(positions)} positions.")
    
    for pos in positions:
        if not isinstance(pos, dict):
            continue
        market_question = pos.get('market_question') or pos.get('question') or pos.get('market', {}).get('question')
        if not market_question:
            continue
            
        print(f"Checking: {market_question}")
        
        # Identify "tomorrow" positions (Feb 17)
        if "February 17" in market_question:
            print(f"Liquidation target: {market_question}")
            
            # Liquidate YES shares
            shares_yes = float(pos.get('shares_yes', 0))
            if shares_yes > 0:
                print(f"Selling {shares_yes} YES shares...")
                res = liquidate_position(pos['market_id'], "yes", shares_yes, "Cutting tomorrow positions per user request")
                print(json.dumps(res, indent=2))
                
            # Liquidate NO shares
            shares_no = float(pos.get('shares_no', 0))
            if shares_no > 0:
                print(f"Selling {shares_no} NO shares...")
                res = liquidate_position(pos['market_id'], "no", shares_no, "Cutting tomorrow positions per user request")
                print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
