#!/usr/bin/env python3
"""
Alert Monitor - Reads trade_alerts.json and writes sendable format
This gets picked up by OpenClaw and sent to Telegram
"""

import json
import os
import time

ALERTS_FILE = "trade_alerts.json"
SENT_ALERTS_FILE = "sent_alerts.json"

def format_alert(alert):
    """Convert alert dict to sendable message format."""
    alert_type = alert.get('type')
    data = alert.get('data', {})
    
    if alert_type == 'trade_executed':
        return f"""🎯 *BTC TRADE EXECUTED*
Strategy: {data.get('strategy', 'Unknown')}
Market: {data.get('market', 'Unknown')}
BTC Price: ${data.get('btc_price', 0):.2f}
Momentum: {data.get('momentum', '?')}
Side: {data.get('side', '?').upper()}
Size: ${data.get('size', 0):.2f}
Entry: ${data.get('entry_price', 0):.4f}
Target: {data.get('target', '?')}"""
    
    elif alert_type == 'position_closed':
        return f"""{data.get('emoji', '?')} *POSITION CLOSED*
Strategy: {data.get('strategy', 'Unknown')}
PnL: ${data.get('pnl', 0):+.2f}
Return: {data.get('return_pct', 0):+.2f}%
Hold Time: {data.get('hold_seconds', 0):.0f}s
Reason: {data.get('reason', 'Unknown')}"""
    
    elif alert_type == 'survival_stats':
        return f"""📊 *4-HOUR SURVIVAL STATS*
Trades: {data.get('trades', 0)}
Wins: {data.get('wins', 0)} | Losses: {data.get('losses', 0)}
Win Rate: {data.get('win_rate', 0):.1f}%
Total PnL: ${data.get('pnl', 0):+.2f}
Balance: ${data.get('balance', 0):.2f}
Uptime: {data.get('uptime_hours', 0):.1f}h
Status: {data.get('position_status', 'Unknown')}"""
    
    elif alert_type == 'system':
        msg = data.get('message', 'Unknown')
        if 'activated' in msg.lower():
            return f"🚀 *SYSTEM* - {msg}"
        elif 'Shutdown' in msg:
            return f"""🛑 *SHUTDOWN*
Trades: {data.get('trades', 'N/A')}
PnL: ${data.get('pnl', 0):+.2f}
Balance: ${data.get('balance', 0):.2f}"""
        else:
            return f"ℹ️ *SYSTEM* - {msg}"
    
    return None

def monitor():
    """Monitor and send unsent alerts."""
    sent = set()
    
    # Load previously sent
    if os.path.exists(SENT_ALERTS_FILE):
        try:
            with open(SENT_ALERTS_FILE, 'r') as f:
                sent = set(json.load(f))
        except:
            pass
    
    while True:
        if os.path.exists(ALERTS_FILE):
            try:
                with open(ALERTS_FILE, 'r') as f:
                    alerts = json.load(f)
                
                for idx, alert in enumerate(alerts):
                    alert_id = f"{alert.get('timestamp')}_{idx}"
                    
                    if alert_id not in sent:
                        msg = format_alert(alert)
                        if msg:
                            print(f"\n{msg}\n")  # Output for OpenClaw to pick up
                            sent.add(alert_id)
                
                # Save sent list
                with open(SENT_ALERTS_FILE, 'w') as f:
                    json.dump(list(sent), f)
            
            except json.JSONDecodeError:
                pass  # File not ready
            except Exception as e:
                print(f"Monitor error: {e}")
        
        time.sleep(3)

if __name__ == "__main__":
    print("Alert monitor started")
    try:
        monitor()
    except KeyboardInterrupt:
        print("Alert monitor stopped")
