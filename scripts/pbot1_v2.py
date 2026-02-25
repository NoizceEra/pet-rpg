import os
import requests
import json
import time
from datetime import datetime

SIMMER_API_KEY = os.getenv("SIMMER_API_KEY")

def log(msg):
    print(f"[{datetime.now()}] {msg}", flush=True)

def get_fast_markets():
    """Fetch active crypto fast markets via Simmer SDK to ensure market availability."""
    url = "https://api.simmer.markets/api/sdk/markets?tags=fast&status=active&limit=50"
    headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        markets = resp.json().get("markets", [])
        # Filter for BTC/ETH sprint markets
        filtered = []
        for m in markets:
            q = m.get("question", "").upper()
            if ("BITCOIN" in q or "ETHEREUM" in q or "BTC" in q or "ETH" in q):
                filtered.append(m)
        return filtered
    except Exception as e:
        log(f"Simmer Discovery Error: {e}")
        return []

def get_clob_ask(token_id):
    """Get the current best ask price from Polymarket CLOB."""
    url = f"https://clob.polymarket.com/price?token_id={token_id}&side=buy"
    try:
        resp = requests.get(url, timeout=5)
        # Add a tiny delay between price fetches to be safe
        time.sleep(0.3)
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
    
    # Position sizing: $3.00 per side to ensure we hit the 5-share minimum
    amount_per_side = 3.0 
    
    payload = {
        "trades": [
            {"market_id": market_id, "side": "yes", "amount": amount_per_side},
            {"market_id": market_id, "side": "no", "amount": amount_per_side}
        ],
        "venue": "polymarket",
        "source": "micro-arb:pbot1",
        "reasoning": f"Micro-arbitrage detected: Combined ASK price ${combined_price:.4f} (< $1.00). Locking in profit via USDC."
    }
    
    log(f"EXECUTING ARB on {question}: Combined ASK ${combined_price:.4f}. Amount: ${amount_per_side} per side.")
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        result = resp.json()
        if result.get("success"):
            log(f"SUCCESS: Arb captured on {market_id}")
            with open("pbot1_v2_captures.log", "a") as f:
                f.write(f"{datetime.now()} | {question} | Combined Ask: {combined_price}\n")
            return True
        else:
            error_msg = result.get('error', 'Unknown Error')
            # Check for detailed results
            if 'results' in result:
                error_msg = ", ".join([r.get('error', 'Error') for r in result['results'] if not r.get('success')])
            
            log(f"Trade Failed: {error_msg}")
            log(f"Full Response: {json.dumps(result)}")
            if "Rate limit" in error_msg:
                retry_after = result.get('retry_after', 40)
                log(f"Rate limit hit. Cooling down for {retry_after}s...")
                time.sleep(retry_after)
            return False
    except Exception as e:
        log(f"Execution Error: {e}")
        return False

def run_v2():
    log("Starting PBot1 v2 (Ask-Based) Execution...")
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
            
            # Threshold: < 1.0
            # Account for 10% taker fee on 'Paid' markets
            effective_combined = combined
            if m.get('is_paid'):
                effective_combined = combined * 1.1
                log(f"  Market is PAID. Effective cost with 10% fee: ${effective_combined:.4f}")

            if effective_combined < 1.0:
                if execute_arb(m['id'], combined, m['question']):
                    executed_count += 1
                    # Simmer rate limit protection - sleep after success
                    time.sleep(32)
            else:
                if m.get('is_paid') and combined < 1.0:
                    log(f"  Arb edge (${combined:.4f}) eaten by fees (${effective_combined:.4f} >= $1.00). Skipping.")
                pass
        else:
            pass
            
    log(f"Finished. Total Arbs Executed: {executed_count}")

if __name__ == "__main__":
    run_v2()
