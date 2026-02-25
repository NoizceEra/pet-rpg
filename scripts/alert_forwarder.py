#!/usr/bin/env python3
"""
Alert Forwarder: Monitors THE_BRAIN's trade_alerts.json and sends to Telegram via OpenClaw message tool.
Runs continuously in background.
"""

import json
import os
import time
import subprocess
from datetime import datetime

ALERTS_FILE = "trade_alerts.json"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ALERTS_PATH = os.path.join(os.path.dirname(SCRIPT_DIR), "trade_alerts.json")

def send_message_to_telegram(message_text: str):
    """Use OpenClaw message tool to send Telegram message."""
    try:
        # Call openclaw message send via subprocess
        cmd = [
            "openclaw", "message", "send",
            "--channel", "telegram",
            "--to", "1251826993",
            "--message", message_text
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Message sent to Telegram")
            return True
        else:
            print(f"⚠️  Message send failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

def format_trade_alert(data):
    """Format trade execution alert."""
    return f"""🎯 *TRADE EXECUTED*
Type: {data.get('strategy', 'Unknown')}
Market: {data.get('market', 'Unknown')[:50]}
Side: {data.get('side', '?').upper()}
Size: ${data.get('size', 0):.2f}
Entry: ${data.get('entry_price', 0):.4f}
Reasoning: {data.get('reasoning', '')[:80]}"""

def format_exit_alert(data):
    """Format position closed alert."""
    emoji = data.get('emoji', '❓')
    return f"""{emoji} *POSITION CLOSED*
Strategy: {data.get('strategy', 'Unknown')}
PnL: ${data.get('pnl', 0):+.2f}
Return: {data.get('return_pct', 0):+.2f}%
Hold Time: {data.get('hold_seconds', 0):.0f}s
Reason: {data.get('reason', 'Unknown')}"""

def format_stats_alert(data):
    """Format 4-hour survival stats."""
    return f"""📊 *4-HOUR SURVIVAL STATS*
Trades: {data.get('trades', 0)}
Wins: {data.get('wins', 0)} | Losses: {data.get('losses', 0)}
Win Rate: {data.get('win_rate', 0):.1f}%
PnL: ${data.get('pnl', 0):+.2f}
Balance: ${data.get('balance', 0):.2f}
Uptime: {data.get('uptime_hours', 0):.1f}h
Status: {data.get('position_status', 'Unknown')}"""

def format_system_alert(data):
    """Format system event."""
    message = data.get('message', 'Unknown event')
    if 'Shutdown' in message:
        return f"""🛑 *SHUTDOWN*
Trades: {data.get('trades', 'N/A')}
PnL: ${data.get('pnl', 0):+.2f}
Final Balance: ${data.get('balance', 0):.2f}"""
    elif 'error' in message.lower():
        return f"""❌ *CRITICAL ERROR*
{message}"""
    else:
        return f"""🚀 *SYSTEM*
{message}"""

def process_alerts():
    """Read alerts file and send unsent ones."""
    if not os.path.exists(ALERTS_PATH):
        return
    
    try:
        with open(ALERTS_PATH, 'r') as f:
            alerts = json.load(f)
        
        unsent = [a for a in alerts if not a.get('sent', False)]
        
        if not unsent:
            return
        
        for alert in unsent:
            alert_type = alert.get('type', 'unknown')
            data = alert.get('data', {})
            
            # Format message based on type
            if alert_type == 'trade_executed':
                msg = format_trade_alert(data)
            elif alert_type == 'position_closed':
                msg = format_exit_alert(data)
            elif alert_type == 'survival_stats':
                msg = format_stats_alert(data)
            elif alert_type == 'system':
                msg = format_system_alert(data)
            else:
                msg = f"Alert: {json.dumps(data)}"
            
            # Send and mark as sent
            if send_message_to_telegram(msg):
                alert['sent'] = True
                print(f"✅ {alert_type} forwarded to Telegram")
            else:
                print(f"⚠️  Failed to send {alert_type}")
                # Don't mark as sent on failure, will retry
        
        # Write back with sent flags updated
        with open(ALERTS_PATH, 'w') as f:
            json.dump(alerts, f, indent=2)
    
    except json.JSONDecodeError:
        pass  # File not ready yet
    except Exception as e:
        print(f"Error processing alerts: {e}")

def run_monitor():
    """Main monitoring loop."""
    print(f"\n{'='*70}")
    print(f"📨 ALERT FORWARDER STARTED")
    print(f"Monitoring: {ALERTS_PATH}")
    print(f"Target: Telegram DM (Noizce)")
    print(f"{'='*70}\n")
    
    while True:
        process_alerts()
        time.sleep(5)  # Check every 5 seconds

if __name__ == "__main__":
    try:
        run_monitor()
    except KeyboardInterrupt:
        print("\n🛑 Alert forwarder stopped.")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
