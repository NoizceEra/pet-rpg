#!/usr/bin/env python3
"""
Check and display trade alerts from THE_BRAIN
Run this to see any new trade alerts
"""

import json
import os

ALERTS_FILE = "trade_alerts.json"
SENT_FILE = ".alerts_sent"

def get_sent():
    """Get timestamps of already-sent alerts."""
    if not os.path.exists(SENT_FILE):
        return set()
    try:
        with open(SENT_FILE, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    except:
        return set()

def mark_sent(timestamp):
    """Mark alert as sent."""
    with open(SENT_FILE, 'a') as f:
        f.write(timestamp + "\n")

def format_alert(alert):
    """Format alert for display."""
    alert_type = alert.get('type')
    data = alert.get('data', {})
    
    if alert_type == 'trade_executed':
        msg = f"""🎯 *TRADE EXECUTED*
Market: {data.get('market', '?')}
Momentum: {data.get('momentum', '?')}
Side: {data.get('side', '?')}
Size: {data.get('size', '?')}
Entry: {data.get('entry', '?')}"""
    
    elif alert_type == 'position_closed':
        msg = f"""{data.get('emoji', '?')} *CLOSED*
PnL: {data.get('pnl', '?')}
Return: {data.get('return', '?')}
Hold: {data.get('hold', '?')}"""
    
    elif alert_type == 'survival_stats':
        msg = f"""📊 *STATS*
Trades: {data.get('trades', '?')} | W: {data.get('wins', '?')} L: {data.get('losses', '?')}
WR: {data.get('win_rate', '?')} | PnL: {data.get('pnl', '?')}
Balance: {data.get('balance', '?')} | Up: {data.get('uptime', '?')}"""
    
    elif alert_type == 'system':
        msg = f"🔔 {data.get('message', '?')}"
    
    else:
        msg = f"❓ Unknown: {json.dumps(data)}"
    
    return msg

def check_alerts():
    """Check for new alerts and print them."""
    if not os.path.exists(ALERTS_FILE):
        print("No alerts file found")
        return
    
    try:
        with open(ALERTS_FILE, 'r') as f:
            alerts = json.load(f)
        
        sent = get_sent()
        found_new = False
        
        for alert in alerts:
            ts = alert.get('timestamp', '')
            
            if ts and ts not in sent:
                msg = format_alert(alert)
                print(f"\n{msg}\n")
                mark_sent(ts)
                found_new = True
        
        if not found_new:
            print("✅ No new alerts")
    
    except json.JSONDecodeError:
        print("⚠️  Alerts file is invalid JSON")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_alerts()
