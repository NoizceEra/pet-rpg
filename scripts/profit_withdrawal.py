#!/usr/bin/env python3
"""
Profit Withdrawal Automation
Auto-send daily profits to cold storage when threshold is hit.
"""

import os
import sys
import json
import requests
from datetime import datetime

SIMMER_API_KEY = os.getenv("SIMMER_API_KEY")
SIMMER_BASE = "https://api.simmer.markets"
COLD_WALLET = None  # TODO: User needs to provide Solana wallet address

# Configuration
DAILY_BASELINE = 51.19  # Starting balance for today (Feb 20)
PROFIT_THRESHOLD_MIN = 20.0  # Trigger at $20 profit
PROFIT_THRESHOLD_MAX = 50.0  # Auto-withdraw at $50 profit
STATE_FILE = "profit_withdrawal_state.json"

def get_current_balance():
    """Fetch current USDC balance from Simmer."""
    url = f"{SIMMER_BASE}/api/sdk/portfolio"
    headers = {"Authorization": f"Bearer {SIMMER_API_KEY}"}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            return float(resp.json().get("balance_usdc", 0.0))
    except Exception as e:
        print(f"Error fetching balance: {e}")
    return 0.0

def load_state():
    """Load withdrawal state (daily baseline, total withdrawn)."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        "daily_baseline": DAILY_BASELINE,
        "total_withdrawn": 0.0,
        "last_withdrawal": None,
        "withdrawals": []
    }

def save_state(state):
    """Save withdrawal state."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def calculate_daily_profit(current_balance, baseline):
    """Calculate profit since daily baseline."""
    return current_balance - baseline

def withdraw_to_cold_storage(amount):
    """
    Send USDC to cold storage wallet.
    TODO: Implement actual Solana transfer via Simmer API or direct wallet.
    """
    if not COLD_WALLET:
        print("⚠️  Cold wallet not configured. Skipping withdrawal.")
        print(f"    Would have withdrawn: ${amount:.2f}")
        return False
    
    # TODO: Implement actual Solana USDC transfer
    # For now, log intent
    print(f"💰 WITHDRAWAL: ${amount:.2f} → {COLD_WALLET}")
    return True

def check_and_withdraw():
    """Main logic: Check profit and trigger withdrawal if needed."""
    state = load_state()
    current_balance = get_current_balance()
    
    if current_balance == 0.0:
        print("❌ Failed to fetch balance. Aborting.")
        return
    
    daily_profit = calculate_daily_profit(current_balance, state["daily_baseline"])
    
    print(f"📊 Balance: ${current_balance:.2f}")
    print(f"📊 Daily Baseline: ${state['daily_baseline']:.2f}")
    print(f"📊 Daily Profit: ${daily_profit:.2f}")
    print(f"📊 Total Withdrawn (Lifetime): ${state['total_withdrawn']:.2f}")
    
    if daily_profit >= PROFIT_THRESHOLD_MIN:
        # Determine withdrawal amount
        if daily_profit >= PROFIT_THRESHOLD_MAX:
            withdraw_amount = PROFIT_THRESHOLD_MAX
            reason = f"Hit max threshold (${PROFIT_THRESHOLD_MAX})"
        else:
            withdraw_amount = daily_profit
            reason = f"Hit min threshold (${PROFIT_THRESHOLD_MIN})"
        
        print(f"\n🎯 WITHDRAWAL TRIGGERED: {reason}")
        
        if withdraw_to_cold_storage(withdraw_amount):
            # Record withdrawal
            state["total_withdrawn"] += withdraw_amount
            state["last_withdrawal"] = datetime.now().isoformat()
            state["withdrawals"].append({
                "date": datetime.now().isoformat(),
                "amount": withdraw_amount,
                "daily_profit": daily_profit,
                "reason": reason
            })
            
            # Reset daily baseline (keep trading with remaining)
            state["daily_baseline"] = current_balance - withdraw_amount
            
            save_state(state)
            print(f"✅ Withdrawal recorded. New baseline: ${state['daily_baseline']:.2f}")
        else:
            print(f"❌ Withdrawal failed.")
    else:
        print(f"\n⏳ Profit below threshold. Need ${PROFIT_THRESHOLD_MIN - daily_profit:.2f} more.")

def reset_daily_baseline():
    """Manually reset daily baseline (e.g., at midnight or after manual adjustment)."""
    state = load_state()
    current_balance = get_current_balance()
    state["daily_baseline"] = current_balance
    save_state(state)
    print(f"✅ Daily baseline reset to ${current_balance:.2f}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        reset_daily_baseline()
    else:
        check_and_withdraw()
