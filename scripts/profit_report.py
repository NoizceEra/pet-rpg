#!/usr/bin/env python3
"""
PROFITABILITY PROJECTION REPORT
Generates scenarios based on current balance and active strategies.
"""

import sys
import math

# Force UTF-8 for Windows console/logs
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Current State
CURRENT_BALANCE = 22.31  # Updated from check
RESERVE_AMOUNT = 1.0
TRADES_PER_DAY = 15      # Conservative estimate (5 arbs, 10 momentum)
CAP_PER_TRADE = 100.0    # Soft cap
MIN_TRADE = 2.0

def calculate_projection(days, roi_per_day):
    balance = CURRENT_BALANCE
    trajectory = []
    
    for day in range(1, days + 1):
        # Daily Compounding
        # Logic: New Balance = Old Balance * (1 + ROI)
        # But we must respect the Cap and Reserve drag
        
        # Calculate roughly how much capital is deployed daily
        # ROI is on the WHOLE account for simplicity in this high-level projection
        
        profit = balance * roi_per_day
        
        # Apply Cap Drag: If 20% of balance > 100, ROI decreases relative to total size
        # (Simplified: Just standard compounding for now until balance > 500)
        
        balance += profit
        trajectory.append((day, balance, profit))
        
    return trajectory

def print_scenario(name, roi, days=7):
    print(f"\n--- {name} Scenario ({roi*100:.1f}% Daily) ---")
    traj = calculate_projection(days, roi)
    
    print(f"{'Day':<5} | {'Balance':<10} | {'Profit':<10}")
    print("-" * 30)
    for day, bal, prof in traj:
        print(f"{day:<5} | ${bal:<9.2f} | +${prof:<9.2f}")
    
    total_profit = traj[-1][1] - CURRENT_BALANCE
    print(f"\nTotal Week Profit: ${total_profit:.2f}")

print(f"📊 PROFITABILITY PROJECTION (Starting Balance: ${CURRENT_BALANCE:.2f})")
print(f"Reserve Locked: ${RESERVE_AMOUNT:.2f} (Trading Liquidity: ${CURRENT_BALANCE - RESERVE_AMOUNT:.2f})")

# Scenarios
# Conservative: 0.8% (Mostly Arbs)
print_scenario("Conservative", 0.008)

# Baseline: 1.5% (Mixed)
print_scenario("Baseline", 0.015)

# Aggressive: 3.0% (High Volatility / Lucky Streaks)
print_scenario("Aggressive", 0.030)
