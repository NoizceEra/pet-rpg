import os
import time
import math
import logging
import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, Tuple, List

# Configuration
LOG_FILE = "boychik_shadow.log"
SHADOW_MODE = False
KELLY_MULTIPLIER = 0.1  # Conservative start for live trading
amount_limit = 3.0  # Cap each trade at $3 USDC to ensure 5-share minimum
LMSR_B = 100  # Liquidity parameter for LMSR
BTC_VOLATILITY_5M = 0.001  # 0.1% approx for 5m sprint
SIMMER_API_KEY = os.getenv("SIMMER_API_KEY")
SIMMER_BASE = "https://api.simmer.markets"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def get_binance_btc() -> Tuple[float, float]:
    """Returns (price, 24h_volume)"""
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
        resp = requests.get(url, timeout=5).json()
        price = float(resp.get('lastPrice', 0))
        volume = float(resp.get('volume', 0))
        return price, volume
    except Exception as e:
        logging.error(f"Binance fetch error: {e}")
        return 0.0, 0.0

def get_coinbase_btc() -> Tuple[float, float]:
    """Returns (price, 24h_volume)"""
    try:
        url = "https://api.exchange.coinbase.com/products/BTC-USD/stats"
        resp = requests.get(url, timeout=5).json()
        return float(resp['last']), float(resp['volume'])
    except Exception as e:
        logging.error(f"Coinbase fetch error: {e}")
        return 0.0, 0.0

def get_kraken_btc() -> Tuple[float, float]:
    """Returns (price, 24h_volume)"""
    try:
        url = "https://api.kraken.com/0/public/Ticker?pair=XBTUSD"
        resp = requests.get(url, timeout=5).json()
        pair_data = resp['result']['XXBTZUSD']
        return float(pair_data['c'][0]), float(pair_data['v'][1])
    except Exception as e:
        logging.error(f"Kraken fetch error: {e}")
        return 0.0, 0.0

def calculate_vwap_belief() -> float:
    sources = [
        get_binance_btc(),
        get_coinbase_btc(),
        get_kraken_btc()
    ]
    total_vol_price = 0.0
    total_vol = 0.0
    for price, vol in sources:
        if price > 0 and vol > 0:
            total_vol_price += price * vol
            total_vol += vol
    return total_vol_price / total_vol if total_vol > 0 else 0.0

def normal_cdf(x: float) -> float:
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

def calculate_posterior(belief_price: float, strike: float, time_left_minutes: float) -> float:
    if time_left_minutes <= 0:
        return 1.0 if belief_price > strike else 0.0
    sigma = BTC_VOLATILITY_5M * math.sqrt(time_left_minutes / 5.0)
    z_score = (strike - belief_price) / (belief_price * sigma)
    return 1.0 - normal_cdf(z_score)

def get_active_sprint_markets() -> List[Dict]:
    url = f"{SIMMER_BASE}/api/sdk/markets?tags=fast&status=active&limit=10"
    headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        return resp.json().get("markets", [])
    except Exception as e:
        logging.error(f"Simmer Discovery Error: {e}")
        return []

def execute_trade(market_id: str, side: str, amount: float, reasoning: str):
    url = f"{SIMMER_BASE}/api/sdk/trade"
    headers = {
        "Authorization": f"Bearer {SIMMER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "market_id": market_id,
        "side": side.lower(),
        "amount": amount,
        "venue": "polymarket",
        "source": "boychik:alpha",
        "reasoning": reasoning
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        result = resp.json()
        if result.get("success"):
            logging.info(f"  LIVE TRADE SUCCESS: {side} on {market_id}")
            return True
        else:
            logging.error(f"  LIVE TRADE FAILED: {result.get('error')}")
            return False
    except Exception as e:
        logging.error(f"  Execution Error: {e}")
        return False

def run_engine_scan():
    logging.info("--- Starting BoyChik Alpha Scan (LIVE USDC) ---")
    belief_price = calculate_vwap_belief()
    if belief_price == 0:
        logging.error("Failed to calculate belief price.")
        return

    logging.info(f"Belief Price (VWAP): ${belief_price:.2f}")

    markets = get_active_sprint_markets()
    if not markets:
        logging.info("No active sprint markets found.")
        return

    for m in markets:
        if "BTC" not in m['question']:
            continue

        # Extract strike price from question (e.g. "BTC > 68500")
        import re
        match = re.search(r'(\d{4,6})', m['question'])
        if not match: continue
        strike = float(match.group(1))
        
        market_price = m.get('current_probability', 0.5)
        resolves_at = datetime.fromisoformat(m['resolves_at'].replace('Z', '+00:00'))
        time_left = (resolves_at - datetime.now(timezone.utc)).total_seconds() / 60.0

        p_belief = calculate_posterior(belief_price, strike, time_left)
        edge = p_belief - market_price
        
        logging.info(f"Market: {m['question']}")
        logging.info(f"  Strike: {strike} | Time Left: {time_left:.1f}m")
        logging.info(f"  Market Price: {market_price:.4f} | Posterior: {p_belief:.4f} | Edge: {edge:.4f}")

        if abs(edge) > 0.05:
            side = "YES" if edge > 0 else "NO"
            prob = p_belief if edge > 0 else (1 - p_belief)
            m_price = market_price if edge > 0 else (1 - market_price)
            
            # Kelly (Net odds b = (1/p) - 1)
            b_odds = (1.0 / m_price) - 1.0
            f_star = (prob * (b_odds + 1) - 1) / b_odds
            # Use small fraction of balance, capped at amount_limit
            fraction = max(0, f_star * KELLY_MULTIPLIER)
            
            # For simplicity with $22 balance, we use a fixed $2 or a tiny fraction
            trade_amount = min(amount_limit, 22.0 * fraction)
            
            if trade_amount < 1.0:
                logging.info(f"  Edge detected but calculated amount ${trade_amount:.2f} too small.")
                continue

            reasoning = f"BoyChik Analysis: VWAP ${belief_price:.2f} vs Strike ${strike}. Posterior ${p_belief:.4f} indicates {edge:+.2f} edge."
            
            if SHADOW_MODE:
                logging.info(f"  SHADOW TRADE: BUY {side} | Amount: ${trade_amount:.2f} | Reasoning: {reasoning}")
            else:
                execute_trade(m['id'], side, trade_amount, reasoning)
                # Rate limit protection
                time.sleep(5)

    logging.info("--- Scan Complete ---")

if __name__ == "__main__":
    run_engine_scan()
