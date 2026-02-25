import os
import requests
import json
import time
from datetime import datetime

SIMMER_API_KEY = os.getenv("SIMMER_API_KEY")

def log(msg):
    print(f"[{datetime.now()}] {msg}", flush=True)

def get_fast_markets():
    """Fetch active crypto fast markets via Simmer SDK."""
    url = "https://api.simmer.markets/api/sdk/markets?tags=fast&status=active&limit=50"
    headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        markets = resp.json().get("markets", [])
        # Filter for BTC/ETH
        filtered = []
        for m in markets:
            q = m.get("question", "").upper()
            if ("BITCOIN" in q or "ETHEREUM" in q or "BTC" in q or "ETH" in q) and ("UP OR DOWN" in q):
                # STRICT FILTER: Today only (Feb 16, 2026)
                if "FEBRUARY 16" in q:
                    filtered.append(m)
                else:
                    # Skip anything not explicitly for today
                    continue
        return filtered
    except Exception as e:
        log(f"Simmer Discovery Error: {e}")
        return []

def get_clob_ask(token_id):
    """Get the current best ask price from Polymarket CLOB."""
    if not token_id: return 0
    url = f"https://clob.polymarket.com/price?token_id={token_id}&side=buy"
    try:
        resp = requests.get(url, timeout=5)
        # Polymarket CLOB rate limit is generous but let's be kind
        time.sleep(0.1)
        data = resp.json()
        if "price" in data:
            return float(data["price"])
        return 0
    except:
        return 0

def execute_arb(market_id, combined_price, question):
    """Execute buy on BOTH sides via Simmer Batch Trades."""
    url = "https://api.simmer.markets/api/sdk/trades/batch"
    headers = {
        "Authorization": f"Bearer {SIMMER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Position sizing: $5.00 per side as per PBot1 default
    amount_per_side = 5.0 
    
    payload = {
        "trades": [
            {"market_id": market_id, "side": "yes", "amount": amount_per_side},
            {"market_id": market_id, "side": "no", "amount": amount_per_side}
        ],
        "venue": "polymarket",
        "source": "micro-arb:pbot1",
        "reasoning": f"Micro-arbitrage detected: Combined ASK price ${combined_price:.4f} (< $1.00). Locking in profit."
    }
    
    log(f"EXECUTING ARB on {question}: Combined ASK ${combined_price:.4f}. Amount: ${amount_per_side} per side.")
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        result = resp.json()
        if result.get("success"):
            log(f"SUCCESS: Arb captured on {market_id}")
            with open("pbot1_v3_captures.log", "a") as f:
                f.write(f"{datetime.now()} | {question} | Combined Ask: {combined_price}\n")
            return True
        else:
            error_msg = result.get('error', 'Unknown Error')
            log(f"Trade Failed: {error_msg}")
            if "Rate limit" in error_msg:
                log("Rate limited. Skipping further trades this cycle.")
                return "RATE_LIMIT"
            return False
    except Exception as e:
        log(f"Execution Error: {e}")
        return False

def run_v3():
    log("Starting PBot1 v3 (Simmer Discovery + Ask-Based) Execution...")
    markets = get_fast_markets()
    log(f"Found {len(markets)} BTC/ETH sprint markets via Simmer.")
    
    executed_count = 0
    for m in markets:
        token_yes = m.get("polymarket_token_id")
        token_no = m.get("polymarket_no_token_id")
        
        if not token_yes or not token_no:
            continue
            
        ask_yes = get_clob_ask(token_yes)
        ask_no = get_clob_ask(token_no)
        
        if ask_yes > 0 and ask_no > 0:
            combined = ask_yes + ask_no
            log(f"Market: {m['question']}")
            log(f"  ASK YES: {ask_yes:.4f} | ASK NO: {ask_no:.4f} | Combined: {combined:.4f}")
            
            # Factor in fees if it's a paid market
            # But the prompt says YES + NO < $1.00.
            if combined < 1.0:
                res = execute_arb(m['id'], combined, m['question'])
                if res == True:
                    executed_count += 1
                elif res == "RATE_LIMIT":
                    break
                # Simmer rate limit protection for batch endpoint is 2/min
                time.sleep(31) 
            else:
                pass
        else:
            pass
            
    log(f"Finished. Total Arbs Executed: {executed_count}")

if __name__ == "__main__":
    run_v3()
