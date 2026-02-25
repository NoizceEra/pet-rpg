import os
import requests
import json

api_key = os.environ.get("SIMMER_API_KEY")
headers = {"Authorization": f"Bearer {api_key}"}

def check_arb(market):
    q = market['question']
    yes_token = market['polymarket_token_id']
    no_token = market['polymarket_no_token_id']
    
    if not yes_token or not no_token:
        return None
        
    try:
        # Get YES best ask
        res_yes = requests.get(f"https://clob.polymarket.com/book?token_id={yes_token}")
        book_yes = res_yes.json()
        best_ask_yes = float(book_yes['asks'][0]['price']) if book_yes.get('asks') else None
        
        # Get NO best ask
        res_no = requests.get(f"https://clob.polymarket.com/book?token_id={no_token}")
        book_no = res_no.json()
        best_ask_no = float(book_no['asks'][0]['price']) if book_no.get('asks') else None
        
        if best_ask_yes is not None and best_ask_no is not None:
            total = best_ask_yes + best_ask_no
            if total < 0.999: # Allowing some margin for fees or slippage
                return {
                    "market_id": market['id'],
                    "question": q,
                    "best_ask_yes": best_ask_yes,
                    "best_ask_no": best_ask_no,
                    "total": total,
                    "profit_pct": (1.0 - total) * 100
                }
    except Exception as e:
        pass
    return None

def main():
    # Search for BTC and ETH sprint markets
    all_markets = []
    for query in ["Bitcoin", "Ethereum"]:
        res = requests.get(f"https://api.simmer.markets/api/sdk/markets?q={query}&status=active&limit=50", headers=headers)
        all_markets.extend(res.json().get('markets', []))
    
    arbs = []
    for m in all_markets:
        # Filter for "sprint" or "Up or Down"
        if "Up or Down" in m['question']:
            arb = check_arb(m)
            if arb:
                arbs.append(arb)
                
    print(json.dumps(arbs, indent=2))

if __name__ == "__main__":
    main()
