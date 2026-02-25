import os
import requests
import json

SIMMER_API_KEY = os.environ.get("SIMMER_API_KEY")

def get_fast_markets():
    headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}
    # Query for BTC and ETH markets
    url = "https://api.simmer.markets/api/sdk/markets?q=Up+or+Down&status=active&limit=50"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Error fetching markets: {resp.status_code}")
        return []
    return resp.json().get("markets", [])

def get_best_ask(token_id):
    url = f"https://clob.polymarket.com/book?token_id={token_id}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return None
    data = resp.json()
    asks = data.get("asks", [])
    if not asks:
        return None
    # Asks are usually sorted by price, but let's be safe
    prices = [float(a['price']) for a in asks]
    return min(prices)

def main():
    markets = get_fast_markets()
    print(f"Found {len(markets)} candidate markets.")
    
    opportunities = []
    for m in markets:
        question = m['question']
        yes_token = m.get('polymarket_token_id')
        no_token = m.get('polymarket_no_token_id')
        
        if not yes_token or not no_token:
            continue
            
        print(f"Checking: {question}")
        yes_ask = get_best_ask(yes_token)
        no_ask = get_best_ask(no_token)
        
        if yes_ask is not None and no_ask is not None:
            combined = yes_ask + no_ask
            print(f"  YES Ask: {yes_ask}, NO Ask: {no_ask}, Combined: {combined}")
            if combined < 1.0:
                print(f"  !!! ARBITRAGE FOUND !!!")
                opportunities.append({
                    "market_id": m['id'],
                    "question": question,
                    "yes_ask": yes_ask,
                    "no_ask": no_ask,
                    "combined": combined
                })
        elif yes_ask is not None:
             print(f"  Only YES Ask: {yes_ask}")
        elif no_ask is not None:
             print(f"  Only NO Ask: {no_ask}")
        else:
            print(f"  No asks available.")
            
    if opportunities:
        print("\nOpportunities Summary:")
        for op in opportunities:
            print(f"- {op['question']}: ${op['combined']} (YES: {op['yes_ask']}, NO: {op['no_ask']})")
    else:
        print("\nNo micro-arbitrage opportunities found.")

if __name__ == "__main__":
    main()
