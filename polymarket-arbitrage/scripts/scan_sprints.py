import os
import json
from datetime import datetime
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds

load_dotenv()

def get_client():
    creds = ApiCreds(
        api_key=os.getenv("POLYMARKET_API_KEY"),
        api_secret=os.getenv("POLYMARKET_API_SECRET"),
        api_passphrase=os.getenv("POLYMARKET_API_PASSPHRASE")
    )
    return ClobClient(
        host="https://clob.polymarket.com",
        key=os.getenv("POLYMARKET_PRIVATE_KEY"),
        chain_id=137,
        creds=creds
    )

def scan_sprint_markets():
    client = get_client()
    print(f"Scanning CLOB for BTC/ETH sprint markets...")
    
    try:
        # Fetch all active markets from CLOB
        resp = client.get_markets()
        markets = resp if isinstance(resp, list) else resp.get('data', [])
    except Exception as e:
        print(f"Error fetching markets: {e}")
        return []

    results = []
    for market in markets:
        question = market.get('question', '').lower()
        # Filter for BTC/ETH sprint markets
        if 'bitcoin' in question or 'ethereum' in question or 'btc' in question or 'eth' in question:
            # Check if it's a "sprint" or short-term market (closing today Feb 17)
            # Sprint markets usually have specific titles or very close expiration
            
            tokens = market.get('tokens', [])
            if len(tokens) < 2:
                continue
                
            prices = [t.get('price') for t in tokens if t.get('price') is not None]
            if len(prices) < len(tokens):
                continue
                
            prob_sum = sum(prices) * 100
            
            if prob_sum < 100:
                implied_profit = 100 - prob_sum
                # User requested 0.05% edge, let's look at raw gap first
                net_profit = implied_profit 
                
                if net_profit >= 0.05:
                    results.append({
                        "title": market.get('question'),
                        "url": f"https://polymarket.com/event/{market.get('condition_id')}",
                        "prob_sum": prob_sum,
                        "net_profit": net_profit,
                        "action": "BUY ALL OUTCOMES",
                        "probabilities": [p*100 for p in prices]
                    })
    
    return results

if __name__ == "__main__":
    arbs = scan_sprint_markets()
    print(json.dumps(arbs, indent=2))
