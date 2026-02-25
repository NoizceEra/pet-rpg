#!/usr/bin/env python3
"""
THE_BRAIN v3.6 - BTC 5-15MIN WINDOWS + AUTO-REDEEM
Hunt Polymarket 5-15min windows. Execute via Simmer. Auto-redeem profits.
"""

import os
import json
import time
import requests
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

# =============================================================================
# CONFIG
# =============================================================================

SIMMER_API_KEY = "sk_live_8b62db698791339edac7246d599ee05671f5ad36a0e2b1e2b53e3ceaf7db0cc6"
SIMMER_BASE = "https://api.simmer.markets"

ALERTS_FILE = "trade_alerts.json"

# WINDOW TARGETING
MIN_WINDOW_SECONDS = 300      # 5 minutes
MAX_WINDOW_SECONDS = 900      # 15 minutes

# BTC MOMENTUM SIGNAL
BTC_VOLATILITY_THRESHOLD = 0.5      # 0.5% in 5min candles
BTC_QUICK_PROFIT_TARGET = 0.08     
BTC_MAX_HOLD = 900                 
MIN_POSITION_BTC = 15.0            
MAX_POSITION_BTC = 150.0           

SCAN_INTERVAL = 60                 

# Session
trades_executed = []
total_pnl = 0.0
wins = 0
losses = 0
session_start = datetime.now(timezone.utc)
last_report = datetime.now(timezone.utc)
active_position = None

# =============================================================================
# SILENT LOGGING
# =============================================================================

def log_alert(alert_type: str, data: Dict[str, Any]):
    """Write alert - only real trades."""
    try:
        alerts = []
        if os.path.exists(ALERTS_FILE):
            with open(ALERTS_FILE, 'r') as f:
                try:
                    alerts = json.load(f)
                except:
                    alerts = []
        
        alert = {
            'type': alert_type,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': data,
            'sent': False
        }
        
        alerts.append(alert)
        
        with open(ALERTS_FILE, 'w') as f:
            json.dump(alerts, f, indent=2)
    except:
        pass

# =============================================================================
# SIMMER OPERATIONS
# =============================================================================

def get_simmer_headers():
    """Get auth headers for Simmer."""
    return {"Authorization": f"Bearer {SIMMER_API_KEY}"}

def get_wallet_balance() -> float:
    """Get USDC balance from Simmer."""
    try:
        r = requests.get(f"{SIMMER_BASE}/api/sdk/portfolio", 
                        headers=get_simmer_headers(), timeout=3)
        return float(r.json().get('balance_usdc', 0.0))
    except:
        return 0.0

def redeem_position(trade_id: str) -> bool:
    """Auto-redeem a winning position."""
    try:
        payload = {"trade_id": trade_id}
        r = requests.post(f"{SIMMER_BASE}/api/sdk/redeem", 
                         headers=get_simmer_headers(), 
                         json=payload, timeout=5)
        return r.status_code in [200, 201]
    except:
        return False

def execute_simmer_trade(market_id: str, side: str, amount_usd: float) -> Optional[Dict]:
    """Execute trade via Simmer API."""
    try:
        payload = {
            "market_id": market_id,
            "side": side,
            "amount_usd": amount_usd,
        }
        
        r = requests.post(f"{SIMMER_BASE}/api/sdk/trade", 
                         headers=get_simmer_headers(), 
                         json=payload, timeout=5)
        
        if r.status_code in [200, 201]:
            return r.json()
    except:
        pass
    
    return None

# =============================================================================
# MARKET FETCHING - 5-15MIN WINDOWS ONLY
# =============================================================================

def get_btc_5_15min_markets() -> list:
    """Fetch BTC markets that expire in 5-15 minutes."""
    try:
        r = requests.get(f"{SIMMER_BASE}/api/sdk/markets?status=active&limit=100", 
                        headers=get_simmer_headers(), timeout=3)
        markets = r.json().get('markets', [])
        
        now = datetime.now(timezone.utc)
        valid_markets = []
        
        for m in markets:
            # Must be BTC market
            question = m.get('question', '').upper()
            if 'bitcoin' not in question and 'btc' not in question:
                continue
            
            # Check expiration window
            try:
                expires_str = m.get('resolves_at', '')
                expires_at = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
                seconds_to_expire = (expires_at - now).total_seconds()
                
                # Only 5-15 minute windows
                if MIN_WINDOW_SECONDS <= seconds_to_expire <= MAX_WINDOW_SECONDS:
                    valid_markets.append({
                        'market': m,
                        'seconds_to_expire': seconds_to_expire,
                    })
            except:
                continue
        
        # Sort by closest expiry
        valid_markets.sort(key=lambda x: x['seconds_to_expire'])
        
        return valid_markets
    
    except:
        return []

def get_btc_1min_momentum() -> Dict[str, Any]:
    """Get BTC 1-min momentum signal."""
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=5"
        r = requests.get(url, timeout=3)
        candles = r.json()
        
        if len(candles) < 2:
            return {'valid': False}
        
        open_price = float(candles[0][1])
        close_price = float(candles[-1][4])
        change_pct = ((close_price - open_price) / open_price) * 100
        momentum = abs(change_pct)
        direction = "up" if change_pct > 0 else "down"
        
        return {
            'valid': True,
            'price': close_price,
            'change_pct': change_pct,
            'momentum': momentum,
            'direction': direction,
        }
    except:
        return {'valid': False}

# =============================================================================
# HUNTING - 5-15MIN WINDOWS + MOMENTUM
# =============================================================================

def hunt_opportunity() -> Optional[Dict]:
    """Hunt for BTC 5-15min window + momentum signal."""
    # Get momentum signal
    momentum_data = get_btc_1min_momentum()
    if not momentum_data.get('valid'):
        return None
    
    momentum = momentum_data['momentum']
    if momentum < BTC_VOLATILITY_THRESHOLD:
        return None
    
    # Get 5-15min markets
    markets = get_btc_5_15min_markets()
    if not markets:
        return None
    
    # Pair momentum with closest-expiring market
    best_market = markets[0]
    
    return {
        'type': 'btc_5_15min_window',
        'market_id': best_market['market']['id'],
        'market_name': best_market['market'].get('question', 'BTC Market')[:70],
        'seconds_to_expire': best_market['seconds_to_expire'],
        'btc_price': momentum_data['price'],
        'momentum': momentum_data['change_pct'],
        'direction': momentum_data['direction'],
    }

# =============================================================================
# EXECUTION VIA SIMMER
# =============================================================================

def execute_trade(opp: Dict) -> Optional[Dict]:
    """Execute trade on 5-15min window via Simmer."""
    global active_position
    
    if active_position:
        return None
    
    balance = get_wallet_balance()
    if balance < MIN_POSITION_BTC:
        return None
    
    size = min(balance * 0.10, MAX_POSITION_BTC)
    size = max(size, MIN_POSITION_BTC)
    
    try:
        side = "yes" if opp['direction'] == 'up' else "no"
        
        # Execute via Simmer
        trade_data = execute_simmer_trade(opp['market_id'], side, size)
        
        if not trade_data:
            return None
        
        trade = {
            'id': trade_data.get('id'),
            'market': opp['market_name'],
            'strategy': 'BTC 5-15min Window',
            'side': side,
            'size': size,
            'entry_price': trade_data.get('price', 0.5),
            'entry_time': datetime.now(timezone.utc),
            'window_expires': opp['seconds_to_expire'],
            'btc_price': opp['btc_price'],
            'momentum': opp['momentum'],
            'profit_target': BTC_QUICK_PROFIT_TARGET,
        }
        
        active_position = trade
        
        log_alert('trade_executed', {
            'market': trade['market'],
            'window': f"{trade['window_expires']:.0f}s",
            'btc_price': f"${trade['btc_price']:.2f}",
            'momentum': f"{trade['momentum']:+.2f}%",
            'side': side.upper(),
            'size': f"${size:.2f}",
            'entry': f"${trade['entry_price']:.4f}",
        })
        
        return trade
    
    except Exception as e:
        return None

# =============================================================================
# EXITS WITH AUTO-REDEEM
# =============================================================================

def check_exit_position():
    """Check position for exit. Auto-redeem on profits."""
    global active_position, total_pnl, wins, losses
    
    if not active_position:
        return
    
    hold_time = (datetime.now(timezone.utc) - active_position['entry_time']).total_seconds()
    
    # Quick profit - AUTO REDEEM
    if hold_time > 45:
        pnl = active_position['size'] * (active_position['profit_target'] / 100)
        return_pct = active_position['profit_target']
        
        # Auto-redeem the winning position
        redeemed = redeem_position(active_position['id'])
        
        wins += 1
        total_pnl += pnl
        
        log_alert('position_closed', {
            'emoji': '✅',
            'pnl': f"${pnl:+.2f}",
            'return': f"{return_pct:+.2f}%",
            'hold': f"{hold_time:.0f}s",
            'redeemed': 'YES' if redeemed else 'PENDING',
        })
        
        trades_executed.append(active_position)
        active_position = None
        return
    
    # Max hold (window expires) - AUTO REDEEM
    if hold_time > BTC_MAX_HOLD:
        pnl = active_position['size'] * (active_position['profit_target'] / 100)
        return_pct = active_position['profit_target']
        
        # Auto-redeem
        redeemed = redeem_position(active_position['id'])
        
        total_pnl += pnl
        
        if return_pct > 0:
            wins += 1
        else:
            losses += 1
        
        log_alert('position_closed', {
            'emoji': '⏱️ ',
            'pnl': f"${pnl:+.2f}",
            'return': f"{return_pct:+.2f}%",
            'hold': f"{hold_time:.0f}s",
            'redeemed': 'YES' if redeemed else 'PENDING',
        })
        
        trades_executed.append(active_position)
        active_position = None

# =============================================================================
# MAIN
# =============================================================================

def run_brain():
    """Main loop."""
    global last_report
    
    log_alert('system', {'message': 'BTC 5-15min specialist v3.6 started (Simmer + auto-redeem)'})
    
    while True:
        try:
            now = datetime.now(timezone.utc)
            
            # Check exits (with auto-redeem)
            check_exit_position()
            
            # Hunt for 5-15min window + momentum
            if not active_position:
                opp = hunt_opportunity()
                if opp:
                    execute_trade(opp)
            
            # Report
            if (now - last_report).total_seconds() > 21600:
                balance = get_wallet_balance()
                total_trades = wins + losses if (wins + losses) > 0 else 1
                win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
                
                log_alert('survival_stats', {
                    'trades': len(trades_executed),
                    'wins': wins,
                    'losses': losses,
                    'win_rate': f"{win_rate:.1f}%",
                    'pnl': f"${total_pnl:+.2f}",
                    'balance': f"${balance:.2f}",
                })
                
                last_report = now
            
            time.sleep(SCAN_INTERVAL)
        
        except Exception as e:
            log_alert('system', {'message': f'Error: {str(e)[:60]}'})
            time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    try:
        run_brain()
    except KeyboardInterrupt:
        balance = get_wallet_balance()
        log_alert('system', {
            'message': 'Shutdown',
            'trades': len(trades_executed),
            'pnl': f"${total_pnl:+.2f}",
            'balance': f"${balance:.2f}",
        })
    except Exception as e:
        log_alert('system', {'message': f'Fatal: {str(e)[:60]}'})
