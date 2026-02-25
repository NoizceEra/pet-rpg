#!/usr/bin/env python3
"""
Monitor and Forward Alerts
Reads trade_alerts.json and sends unsent alerts via JSON messages
that the gateway can forward to Telegram.
"""

import json
import os
import time
import hashlib

ALERTS_FILE = "trade_alerts.json"
FORWARDED_FILE = "forwarded_alerts.json"

def get_forwarded():
    """Get list of already-forwarded alerts."""
    if not os.path.exists(FORWARDED_FILE):
        return set()
    try:
        with open(FORWARDED_FILE, 'r') as f:
            return set(json.load(f))
    except:
        return set()

def save_forwarded(alert_hashes):
    """Save forwarded alert hashes."""
    with open(FORWARDED_FILE, 'w') as f:
        json.dump(list(alert_hashes), f)

def get_alert_hash(alert):
    """Get unique hash of alert."""
    data = json.dumps({
        'type': alert.get('type'),
        'timestamp': alert.get('timestamp'),
        'data': alert.get('data'),
    }, sort_keys=True)
    return hashlib.md5(data.encode()).hexdigest()

def format_message(alert):
    """Format alert for display."""
    alert_type = alert.get('type')
    data = alert.get('data', {})
    
    if alert_type == 'trade_executed':
        return f"""🎯 *BTC TRADE EXECUTED*
Market: {data.get('market', 'Unknown')}
Momentum: {data.get('momentum', '?')}
Side: {data.get('side', '?')}
Size: {data.get('size', '?')}
Entry: {data.get('entry', '?')}"""
    
    elif alert_type == 'position_closed':
        return f"""{data.get('emoji', '?')} *POSITION CLOSED*
PnL: {data.get('pnl', '?')}
Return: {data.get('return', '?')}
Hold: {data.get('hold', '?')}"""
    
    elif alert_type == 'survival_stats':
        return f"""📊 *4-HOUR STATS*
Trades: {data.get('trades', '?')}
Win/Loss: {data.get('wins', '?')}/{data.get('losses', '?')}
WR: {data.get('win_rate', '?')}
PnL: {data.get('pnl', '?')}
Balance: {data.get('balance', '?')}"""
    
    elif alert_type == 'system':
        msg = data.get('message', 'Unknown')
        if 'shutdown' in msg.lower():
            return f"""🛑 *SHUTDOWN*
{msg}"""
        elif 'active' in msg.lower():
            return f"🚀 *{msg}*"
        else:
            return f"ℹ️ {msg}"
    
    return None

def check_and_output():
    """Check for new alerts and output them."""
    if not os.path.exists(ALERTS_FILE):
        return
    
    forwarded = get_forwarded()
    new_hashes = set(forwarded)
    
    try:
        with open(ALERTS_FILE, 'r') as f:
            alerts = json.load(f)
        
        for alert in alerts:
            alert_hash = get_alert_hash(alert)
            
            if alert_hash not in forwarded:
                msg = format_message(alert)
                if msg:
                    # Output message for OpenClaw to capture
                    print(f"\n[TRADE_ALERT]")
                    print(msg)
                    print(f"[/TRADE_ALERT]\n")
                    
                    new_hashes.add(alert_hash)
    
    except json.JSONDecodeError:
        pass
    except Exception as e:
        print(f"[MONITOR_ERROR] {e}", flush=True)
    
    # Update forwarded list
    save_forwarded(new_hashes)

if __name__ == "__main__":
    print("Alert monitor started", flush=True)
    while True:
        try:
            check_and_output()
            time.sleep(3)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[MONITOR_ERROR] {e}", flush=True)
            time.sleep(5)
    
    print("Alert monitor stopped", flush=True)
