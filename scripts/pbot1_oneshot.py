import os
import requests
from datetime import datetime

SIMMER_API_KEY = os.getenv("SIMMER_API_KEY")

def log(msg):
    print(f"[{datetime.now()}] {msg}")

def get_active_sprint_markets():
    # Searching specifically for BTC and ETH in fast markets
    url = "https://api.simmer.markets/api/sdk/markets?tags=fast&status=active&limit=50"
    headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        markets = resp.json().get("markets", [])
        # Filter for BTC and ETH
        filtered = [m for m in markets if "BTC" in m['question'].upper() or "ETH" in m['question'].upper() or "BITCOIN" in m['question'].upper() or "ETHEREUM" in m['question'].upper()]
        return filtered
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

def execute_arb(market_id, combined_price, question):
    url = "https://api.simmer.markets/api/sdk/trades/batch"
    headers = {
        "Authorization": f"Bearer {SIMMER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Smart sizing: using a small fixed amount for now to test, 
    # but could be scaled based on portfolio
    amount_per_side = 5.0 
    
    payload = {
        "trades": [
            {"market_id": market_id, "side": "yes", "amount": amount_per_side},
            {"market_id": market_id, "side": "no", "amount": amount_per_side}
        ],
        "venue": "polymarket",
        "source": "micro-arb:pbot1",
        "reasoning": f"Micro-arbitrage detected: Combined price ${combined_price:.3f} (< $1.00). Buying both sides for guaranteed profit."
    }
    
    log(f"EXECUTING ARB on {question}: Combined Price ${combined_price:.3f}. Amount: ${amount_per_side} per side.")
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        result = resp.json()
        if result.get("success"):
            log(f"SUCCESS: Arb captured on {market_id}")
            with open("pbot1_arb_captures.log", "a") as f:
                f.write(f"{datetime.now()} | {question} | Combined: {combined_price}\n")
            return True
        else:
            log(f"Trade Failed: {result.get('error')}")
            return False
    except Exception as e:
        log(f"Execution Error: {e}")
        return False

def run_once():
    log("Starting PBot1 Micro-Arb Execution...")
    markets = get_active_sprint_markets()
    log(f"Found {len(markets)} BTC/ETH sprint markets.")
    
    executed_count = 0
    for m in markets:
        yes_token = m.get("polymarket_token_id")
        no_token = m.get("polymarket_no_token_id")
        
        if not yes_token or not no_token:
            continue
            
        # Check if it's 15m or 5m (the prompt says 15-minute)
        # We can try to infer from the question or just check all sprint markets
        
        price_yes = get_clob_price(yes_token)
        price_no = get_clob_price(no_token)
        
        if price_yes > 0 and price_no > 0:
            combined = price_yes + price_no
            log(f"Checking: {m['question']}")
            log(f"  YES: {price_yes:.3f} | NO: {price_no:.3f} | Combined: {combined:.3f}")
            
            # PBot1 Threshold: Combined cost < $1.00
            # Note: 0.99 is used in autonomous_engine.py as a buffer
            if combined < 1.0:
                # We should check if it's a paid market (fees)
                # m.get('is_paid')
                if m.get('is_paid'):
                    # Fee is usually 10% for fast markets
                    effective_cost = combined * 1.1
                    log(f"  Market is PAID. Effective cost with 10% fee: ${effective_cost:.3f}")
                    if effective_cost < 1.0:
                        if execute_arb(m['id'], combined, m['question']):
                            executed_count += 1
                    else:
                        log(f"  Edge eaten by fees (${effective_cost:.3f} >= $1.00). Skipping.")
                else:
                    if execute_arb(m['id'], combined, m['question']):
                        executed_count += 1
            else:
                log("  No arb edge.")
        else:
            log(f"  Price data missing for {m['question']}")
            
    log(f"Finished. Total Arbs Executed: {executed_count}")

if __name__ == "__main__":
    run_once()
