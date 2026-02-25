#!/usr/bin/env python3
import os
import requests
import logging

SIMMER_API_KEY = os.getenv("SIMMER_API_KEY")
SIMMER_BASE = "https://api.simmer.markets"

import sys
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', stream=sys.stdout)

def execute_simmer_trade(market_id, side, action="sell", shares=None):
    url = f"{SIMMER_BASE}/api/sdk/trade"
    headers = {
        "Authorization": f"Bearer {SIMMER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "market_id": market_id,
        "side": side.lower(),
        "venue": "polymarket",
        "source": "manual_flush",
        "reasoning": "Flush both sides",
        "action": action,
        "shares": shares
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        res = resp.json()
        if res.get("success"):
            logging.info(f"✅ FLUSHED {side.upper()} on {market_id}")
            return True
        else:
            logging.error(f"❌ FLUSH FAILED: {res.get('error')}")
            return False
    except Exception as e:
        logging.error(f"Flush Error: {e}")
        return False

def flush_both():
    print("Fetching positions...")
    url = f"{SIMMER_BASE}/api/sdk/positions"
    headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {resp.status_code}")
        data = resp.json()
        positions = data.get("positions", [])
        print(f"Found {len(positions)} positions.")
        for p in positions:
            shares_yes = p.get("shares_yes", 0)
            shares_no = p.get("shares_no", 0)
            if shares_yes > 0 and shares_no > 0:
                logging.info(f"⚠️ 'Both' position found in {p['question']} ({p['market_id']})")
                if p.get("redeemable"):
                    logging.info("Market is redeemable. Attempting redemption instead of flush.")
                    for side in ["yes", "no"]:
                        if p.get(f"shares_{side}", 0) > 0:
                            requests.post(f"{SIMMER_BASE}/api/sdk/redeem", json={"market_id": p['market_id'], "side": side}, headers=headers)
                            logging.info(f"Redeemed {side.upper()}")
                else:
                    logging.info(f"Flushing YES: {shares_yes}")
                    execute_simmer_trade(p['market_id'], "yes", shares=shares_yes)
                    logging.info(f"Flushing NO: {shares_no}")
                    execute_simmer_trade(p['market_id'], "no", shares=shares_no)
            else:
                logging.info(f"OK: {p['question']} (Yes: {shares_yes}, No: {shares_no})")
    except Exception as e:
        logging.error(f"Position Check Error: {e}")

if __name__ == "__main__":
    print("Starting flush_both...")
    flush_both()
    print("Done.")
