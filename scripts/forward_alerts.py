#!/usr/bin/env python3
"""
Forward Alerts - Reads trade_alerts.json and outputs formatted messages
Run this periodically to check for and forward unsent alerts
"""

import json
import os
import sys

ALERTS_FILE = "trade_alerts.json"
SENT_FILE = "alerts_sent.txt"

def get_sent_alerts():
    """Get list of already-sent alert timestamps."""
    if not os.path.exists(SENT_FILE):
        return set()
    try:
        with open(SENT_FILE, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    except:
        return set()

def save_sent_alert(timestamp):
    """Mark alert as sent."""
    with open(SENT_FILE, 'a') as f:
        f.write(f"{timestamp}\n")

def format_alert(alert):
    """Convert alert to message format."""
    alert_type = alert.get('type')
    data = alert.get('data', {})
    
    if alert_type == 'trade_executed':
        return f"""🎯 *BTC TRADE EXECUTED*
Market: {data.get('market', 'Unknown')}
Momentum: {data.get('momentum', '?')}
Side: {data.get('side', '?').upper()}
Size: ${data.get('size', 0):.2f}
Entry: ${data.get('entry_price', 0):.4f}
Target: {data.get('target', '?')}"""
    
    elif alert_type == 'position_closed':
        return f"""{data.get('emoji', '?')} *POSITION CLOSED*
PnL: ${data.get('pnl', 0):+.2f}
Return: {data.get('return_pct', 0):+.2f}%
Hold: {data.get('hold_seconds', 0):.0f}s
Reason: {data.get('reason', 'Unknown')}"""
    
    elif alert_type == 'survival_stats':
        return f"""📊 *4-HOUR STATS*
Trades: {data.get('trades', 0)} | W: {data.get('wins', 0)} | L: {data.get('losses', 0)}
WR: {data.get('win_rate', 0):.1f}% | PnL: ${data.get('pnl', 0):+.2f}
Balance: ${data.get('balance', 0):.2f} | Up: {data.get('uptime_hours', 0):.1f}h"""
    
    elif alert_type == 'system':
        msg = data.get('message', '?')
        if 'activated' in msg.lower():
            return f"🚀 *SYSTEM* - {msg}"
        elif 'Shutdown' in msg:
            return f"""🛑 *SHUTDOWN*
Trades: {data.get('trades', 'N/A')} | PnL: ${data.get('pnl', 0):+.2f}"""
        else:
            return f"ℹ️ {msg}"
    
    return None

def check_and_forward():
    """Check for unsent alerts and output them."""
    if not os.path.exists(ALERTS_FILE):
        return
    
    sent = get_sent_alerts()
    
    try:
        with open(ALERTS_FILE, 'r') as f:
            alerts = json.load(f)
        
        for alert in alerts:
            ts = alert.get('timestamp', '')
            
            if ts and ts not in sent:
                msg = format_alert(alert)
                if msg:
                    # Output the message (for OpenClaw to capture and forward)
                    print(msg)
                    print("---")  # Separator
                    sys.stdout.flush()
                    
                    # Mark as sent
                    save_sent_alert(ts)
    
    except json.JSONDecodeError:
        pass
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    check_and_forward()
