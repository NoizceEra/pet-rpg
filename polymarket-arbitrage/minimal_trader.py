#!/usr/bin/env python3
"""
MINIMAL WORKING TRADER - No fluff, just trades
30-minute build for live testing

Features:
- Gets markets with token IDs
- Checks orderbooks for real arbitrage
- Places actual orders if found
- $1-2 position sizes for safety
- Real-time logging
"""

import os
import sys
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs

load_dotenv()

# Safety limits
MAX_POSITION_SIZE = 2.0  # $2 max per trade for testing
MIN_EDGE = 2.0  # 2% minimum profit
TAKER_FEE = 0.02  # 2% fee
MAX_TRADES = 3  # Stop after 3 trades for safety
# Initialize client
print("[INIT] Setting up Polymarket client...")
try:
    creds = ApiCreds(
        api_key=os.getenv("POLYMARKET_API_KEY"),
        api_secret=os.getenv("POLYMARKET_API_SECRET"),
        api_passphrase=os.getenv("POLYMARKET_API_PASSPHRASE")
    )
    
    client = ClobClient(
        host="https://clob.polymarket.com",
        key=os.getenv("POLYMARKET_PRIVATE_KEY"),
        chain_id=137,
        creds=creds
    )
    print("[OK] Client initialized")
except Exception as e:
    print(f"[FATAL] Client setup failed: {e}")
    sys.exit(1)


def log(msg):
    """Simple timestamped logging"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def find_arbitrage():
    """
    Find real arbitrage opportunities.
    Returns: (market, tokens, ask_prices, edge_pct) or None
    """
    log("Fetching markets with token data...")
    
    # Get markets - using the sampling endpoint but we'll filter for ones with tokens
    try:
        resp = client.get_sampling_markets()
        markets = resp.get('data', []) if isinstance(resp, dict) else []
        log(f"Got {len(markets)} markets to scan")
    except Exception as e:
        log(f"ERROR fetching markets: {e}")
        return None    
    # Scan for arbitrage
    for i, market in enumerate(markets[:100]):  # Check first 100
        try:
            question = market.get('question', 'Unknown')[:50]
            tokens = market.get('tokens', [])
            
            if len(tokens) < 2:
                continue
            
            # Get token IDs
            token_ids = [t.get('token_id') for t in tokens if t.get('token_id')]
            if len(token_ids) != len(tokens):
                continue  # Missing token IDs
            
            # Fetch orderbooks for all outcomes
            ask_prices = []
            books_ok = True
            
            for token_id in token_ids:
                try:
                    book = client.get_order_book(token_id)
                    if not book or not book.get('asks'):
                        books_ok = False
                        break
                    
                    # Get best ask (what we pay)
                    best_ask = float(book['asks'][0]['price'])
                    ask_prices.append(best_ask)
                except:
                    books_ok = False
                    break
            
            if not books_ok or len(ask_prices) != len(tokens):
                continue
            
            # Check for arbitrage
            total_cost = sum(ask_prices)
            total_fees = TAKER_FEE * len(tokens)
            net_profit = 1.0 - (total_cost + total_fees)
            edge_pct = net_profit * 100
            
            if edge_pct >= MIN_EDGE:
                log(f"[ARBITRAGE] {question}")
                log(f"  Outcomes: {len(tokens)}")
                log(f"  Ask prices: {[f'${p:.3f}' for p in ask_prices]}")
                log(f"  Total cost: ${total_cost:.3f}")
                log(f"  Edge: {edge_pct:.2f}%")
                return (market, tokens, ask_prices, edge_pct)
            
            if (i + 1) % 20 == 0:
                log(f"  Scanned {i+1} markets...")
        
        except Exception as e:
            continue
    
    log("No arbitrage found in scan")
    return None


def execute_trade(market, tokens, ask_prices, edge_pct):
    """
    Execute arbitrage by buying all outcomes.
    Returns: True if successful, False otherwise
    """
    question = market.get('question', 'Unknown')[:50]
    log(f"[EXECUTE] Attempting trade on: {question}")
    log(f"  Edge: {edge_pct:.2f}%")
    
    # Calculate position size per outcome
    num_outcomes = len(tokens)
    total_cost = sum(ask_prices)
    
    # Allocate proportionally to prices
    allocations = []
    for i, (token, ask) in enumerate(zip(tokens, ask_prices)):
        # Size proportional to price
        size_usd = MAX_POSITION_SIZE * (ask / total_cost)
        size_shares = size_usd / ask  # Convert USD to shares
        
        allocations.append({
            'token_id': token['token_id'],
            'outcome': token['outcome'],
            'price': ask,
            'size_usd': size_usd,
            'size_shares': size_shares
        })
        
        log(f"  Leg {i+1}: Buy {size_shares:.2f} shares of '{token['outcome']}' @ ${ask:.3f}")    
    # Execute each leg
    filled_legs = []
    
    for alloc in allocations:
        try:
            log(f"  Placing order for {alloc['outcome']}...")
            
            # Create order
            order = OrderArgs(
                token_id=alloc['token_id'],
                price=alloc['price'] * 1.05,  # 5% slippage buffer
                size=alloc['size_shares'],
                side="BUY",
                fee_rate_bps=200  # 2%
            )
            
            # Submit order
            resp = client.create_order(order)
            
            if not resp or 'orderID' not in resp:
                log(f"  [FAIL] Order submission failed for {alloc['outcome']}")
                # Try to cancel previous legs
                for prev_order_id in filled_legs:
                    try:
                        client.cancel_order(prev_order_id)
                    except:
                        pass
                return False
            
            order_id = resp['orderID']
            filled_legs.append(order_id)
            log(f"  [OK] Order placed: {order_id}")            
            # Wait briefly for fill
            time.sleep(1)
            
        except Exception as e:
            log(f"  [FAIL] Error placing order: {e}")
            # Try to cancel previous legs
            for prev_order_id in filled_legs:
                try:
                    client.cancel_order(prev_order_id)
                except:
                    pass
            return False
    
    log(f"[SUCCESS] All {len(filled_legs)} orders placed!")
    log(f"  Expected profit: ${MAX_POSITION_SIZE * (edge_pct/100):.2f}")
    
    # Log to file
    trade_record = {
        'timestamp': datetime.now().isoformat(),
        'market': question,
        'edge_pct': edge_pct,
        'position_size': MAX_POSITION_SIZE,
        'num_legs': len(filled_legs),
        'order_ids': filled_legs,
        'status': 'EXECUTED'
    }
    
    with open('trade_log.json', 'a') as f:
        f.write(json.dumps(trade_record) + '\n')
    
    return True


def main():
    """Main trading loop"""
    log("=" * 60)
    log("MINIMAL WORKING TRADER - LIVE MODE")
    log("=" * 60)
    log(f"Max position: ${MAX_POSITION_SIZE} per trade")
    log(f"Min edge: {MIN_EDGE}%")
    log(f"Safety limit: {MAX_TRADES} trades")
    log("=" * 60)
    
    trades_executed = 0
    scan_count = 0
    
    while trades_executed < MAX_TRADES:
        scan_count += 1
        log(f"\n[SCAN {scan_count}] Looking for arbitrage...")
        
        # Find opportunity
        result = find_arbitrage()
        
        if result:
            market, tokens, ask_prices, edge_pct = result
            
            # Execute trade
            success = execute_trade(market, tokens, ask_prices, edge_pct)
            
            if success:
                trades_executed += 1
                log(f"\n[PROGRESS] Trades executed: {trades_executed}/{MAX_TRADES}")
            else:
                log(f"[SKIP] Trade failed, continuing scan...")
        
        else:
            log("[NO ARB] No opportunities found this scan")        
        # Wait before next scan
        if trades_executed < MAX_TRADES:
            wait_time = 30
            log(f"Waiting {wait_time}s before next scan...")
            time.sleep(wait_time)
    
    log("\n" + "=" * 60)
    log(f"[COMPLETE] Executed {trades_executed} trades")
    log("Check trade_log.json for details")
    log("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n[STOPPED] User interrupted")
    except Exception as e:
        log(f"\n[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()