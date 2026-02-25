#!/usr/bin/env python3
"""
Team Pinchie Alert System
Formats and sends high-signal trading alerts to Telegram.
"""

import os
import sys
import json
import requests
from datetime import datetime

# Configuration
TELEGRAM_BOT_TOKEN = "7547000845:AAH_QxT716v-U1eLq-f7A_M245-uN8Y7_YI"
TELEGRAM_CHAT_ID = "1251826993"

def send_native_message(text):
    """Fallback to console output which can be caught by the agent."""
    # Ensure UTF-8 output even on Windows/PowerShell
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout.buffer.write(f"TELEGRAM_ALERT_STAGING: {text}\n".encode('utf-8'))
        sys.stdout.buffer.flush()
    else:
        print(f"TELEGRAM_ALERT_STAGING: {text}")

def get_current_cash():
    """Mock/Stub for now, or read from a state file if available."""
    # In a real scenario, this would call the portfolio API or read a local log
    return 10.88

def send_alert(alert_data):
    """
    Formats the arb data into the Pinchie-approved template.
    
    Expected alert_data:
    {
        "title": "Market Title",
        "url": "https://polymarket.com/...",
        "type": "Math Arb / Long-shot",
        "entry_price": "$0.017",
        "shares": "58.82",
        "potential_payout": "$58.82",
        "profit_pct": "12.0%",
        "blockchain": "Solana / Polymarket",
        "amount_entered": "$10.00"
    }
    """
    
    cash_balance = get_current_cash()
    
    message = (
        f"⚡ *Team Pinchie Trade Alert!* ⚡\n\n"
        f"📍 *Market:* {alert_data.get('title', 'Unknown')}\n"
        f"⛓️ *Network:* {alert_data.get('blockchain', 'Polymarket')}\n"
        f"🏷️ *Type:* {alert_data.get('type', 'Arbitrage')}\n\n"
        f"💵 *Amount Entered:* {alert_data.get('amount_entered', 'N/A')}\n"
        f"💰 *Entry Price:* {alert_data.get('entry_price', 'N/A')}\n"
        f"📊 *Shares:* {alert_data.get('shares', 'N/A')}\n"
        f"📈 *Profit:* {alert_data.get('profit_pct', 'N/A')}\n"
        f"💎 *Potential Payout:* {alert_data.get('potential_payout', 'N/A')}\n\n"
        f"🏦 *Total Cash Balance:* ${cash_balance:.2f}\n\n"
        f"🔗 [VIEW TRADE & EXECUTE]({alert_data.get('url', '#')})"
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Alert sent successfully!")
        return True
    except Exception as e:
        print(f"Failed to send alert: {e}")
        send_native_message(message) # Fallback to agent logs
        return False

if __name__ == "__main__":
    # Test alert if run directly
    test_data = {
        "title": "US city insolvent in 2026",
        "url": "https://polymarket.com/event/will-a-us-city-become-insolvent-in-2026",
        "type": "Risk Harvest / Long-shot",
        "entry_price": "$0.014",
        "shares": "71.42",
        "potential_payout": "$100.00",
        "profit_pct": "Asymmetric (Low Risk)"
    }
    send_alert(test_data)
