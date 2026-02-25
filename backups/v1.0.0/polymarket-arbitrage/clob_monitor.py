#!/usr/bin/env python3
"""
Polymarket CLOB API Arbitrage Scanner & Executor.
Uses the real API to find and execute math arbs.
"""

import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs
from py_clob_client.constants import BUY

load_dotenv()

# Config
MIN_NET_EDGE = 3.0 # %
MAX_POSITION_SIZE = 0.50 # USD
MIN_POSITION_SIZE = 0.10 # USD
TAKER_FEE = 0.02 # 2% per leg

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

def scan_and_trade(client):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Scanning CLOB markets...")
    
    # 1. Fetch Markets
    try:
        resp = client.get_sampling_markets()
        markets = resp if isinstance(resp, list) else resp.get('data', [])
    except Exception as e:
        print(f"Error fetching markets: {e}")
        return

    for market in markets:
        if not market.get('active') or market.get('closed'):
            continue
            
        tokens = market.get('tokens', [])
        if len(tokens) < 2:
            continue
            
        # Calculate prob sum
        prices = [t.get('price') for t in tokens if t.get('price') is not None]
        if len(prices) < len(tokens):
            continue
            
        prob_sum = sum(prices) * 100
        
        if prob_sum < 100:
            implied_profit = 100 - prob_sum
            # Net profit after fees on all legs
            net_profit = implied_profit - (TAKER_FEE * 100 * len(tokens))
            
            if net_profit >= MIN_NET_EDGE:
                print(f"💰 ARB FOUND: {market.get('question')} | Net Profit: {net_profit:.2f}%")
                
                # Execute!
                # Dynamic sizing based on volume/risk (Simplified for now)
                size = MAX_POSITION_SIZE 
                
                # For each token, place a buy order
                for token in tokens:
                    token_id = token['token_id']
                    # Simplified: bet enough to get equal payout
                    # amount_to_bet = (size * (token['price'] * 100 / prob_sum)) / 100
                    # For $0.50 total, let's just split for now
                    leg_size = size / len(tokens)
                    
                    print(f"   -> Buying {token['outcome']} (${leg_size:.2f})")
                    
                    # TODO: Real order placement
                    # order = OrderArgs(
                    #     price=token['price'],
                    #     size=leg_size / token['price'],
                    #     side=BUY,
                    #     token_id=token_id
                    # )
                    # client.create_order(order)
                
                # Log to forensics
                log_file = rf"C:\Users\vclin_jjufoql\.openclaw\workspace\polymarket-arbitrage\forensics\trade_{int(time.time())}.json"
                with open(log_file, "w") as f:
                    json.dump({
                        "timestamp": datetime.now().isoformat(),
                        "market": market.get('question'),
                        "net_profit": net_profit,
                        "status": "LOGGED_WIP"
                    }, f)

def main():
    client = get_client()
    while True:
        try:
            scan_and_trade(client)
        except Exception as e:
            print(f"Loop error: {e}")
        time.sleep(60)

if __name__ == "__main__":
    main()
