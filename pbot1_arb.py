import os
import requests
import json
from datetime import datetime

SIMMER_API_KEY = "sk_live_67cde9c17d16218b380e3452a7dbd4d5711b4a1a3c59a58e3d838aa93248a1b0"
PBOT1_WALLET = "0x88f46b9e5d86b4fb85be55ab0ec4004264b9d4db"
BASE_URL = "https://api.simmer.markets/api/sdk"
CLOB_URL = "https://clob.polymarket.com/book"

headers = {
    "Authorization": f"Bearer {SIMMER_API_KEY}",
    "Content-Type": "application/json"
}

def get_sprint_markets():
    markets = []
    for query in ["Bitcoin Up or Down", "Ethereum Up or Down"]:
        url = f"{BASE_URL}/markets?q={query}&status=active&limit=50"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                markets.extend(data)
            elif isinstance(data, dict) and 'markets' in data:
                markets.extend(data['markets'])
    
    return markets

def get_best_ask(token_id):
    if not token_id:
        return None
    url = f"{CLOB_URL}?token_id={token_id}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            asks = data.get('asks', [])
            if asks:
                return min(float(a['price']) for a in asks)
    except Exception as e:
        print(f"Error fetching orderbook for {token_id}: {e}")
    return None

def main():
    print(f"Checking PBot1 Micro-Arb Strategy at {datetime.now()}")
    
    sprint_markets = get_sprint_markets()
    print(f"Scanning {len(sprint_markets)} sprint markets...")
    
    opportunities = []
    for m in sprint_markets:
        question = m['question']
        yes_token = m.get('polymarket_token_id')
        no_token = m.get('polymarket_no_token_id')
        
        if not yes_token or not no_token:
            continue
            
        ask_yes = get_best_ask(yes_token)
        ask_no = get_best_ask(no_token)
        
        if ask_yes and ask_no:
            combined_cost = ask_yes + ask_no
            print(f"Market: {question}")
            print(f"  YES Ask: {ask_yes:.4f} | NO Ask: {ask_no:.4f} | Sum: {combined_cost:.4f}")
            
            if combined_cost < 1.00:
                print(f"  !!! ARB DETECTED !!! Edge: {1.00 - combined_cost:.4f}")
                opportunities.append({
                    "market": m,
                    "ask_yes": ask_yes,
                    "ask_no": ask_no,
                    "sum": combined_cost,
                    "edge": 1.00 - combined_cost
                })
        else:
            print(f"Market: {question} (Incomplete orderbook data)")

    if opportunities:
        print(f"\nFound {len(opportunities)} arbitrage opportunities!")
        for opp in opportunities:
            # Execute trades autonomously via Simmer proxy with smart sizing
            # Smart sizing: User didn't specify, but I'll use a conservative amount like 10 USDC per side for now.
            # Or proportional to edge.
            
            m = opp['market']
            market_id = m['id']
            edge = opp['edge']
            
            # sizing: 10 USDC * (edge * 100) or similar? 
            # Let's stick to 10 USDC per side for safety if edge is confirmed.
            amount = 10.0 
            
            print(f"Executing Arb on: {m['question']}")
            
            # Buy YES
            res_yes = requests.post(f"{BASE_URL}/trade", headers=headers, json={
                "market_id": market_id,
                "side": "yes",
                "amount": amount,
                "venue": "polymarket",
                "source": "sdk:pbot1-arb",
                "reasoning": f"Micro-arbitrage strategy. Combined YES+NO cost is ${opp['sum']:.4f}. Locking in guaranteed ${opp['edge']:.4f} edge."
            })
            
            # Buy NO
            res_no = requests.post(f"{BASE_URL}/trade", headers=headers, json={
                "market_id": market_id,
                "side": "no",
                "amount": amount,
                "venue": "polymarket",
                "source": "sdk:pbot1-arb",
                "reasoning": f"Micro-arbitrage strategy. Combined YES+NO cost is ${opp['sum']:.4f}. Locking in guaranteed ${opp['edge']:.4f} edge."
            })
            
            print(f"  YES Trade: {res_yes.status_code} {res_yes.text}")
            print(f"  NO Trade: {res_no.status_code} {res_no.text}")
    else:
        print("\nNo arbitrage opportunities found at this time.")

if __name__ == "__main__":
    main()
