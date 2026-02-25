#!/usr/bin/env python3
"""
Simple Polymarket arbitrage scanner
Usage: python run_scan.py [--min-edge 3.0] [--alert]
"""

import subprocess
import json
import argparse
from datetime import datetime
import os

def run_scan(min_edge=3.0, alert=False):
    """Run a complete arbitrage scan"""
    print(f"Polymarket Arbitrage Scanner - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Fetch fresh markets
    print("Fetching markets...")
    result = subprocess.run([
        'python', 'scripts/fetch_markets.py', 
        '--output', 'markets.json'
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error fetching markets: {result.stderr}")
        return False
    
    # Parse fetch results
    try:
        fetch_data = json.loads(result.stdout.strip().split('\n')[-1])
        market_count = fetch_data.get('market_count', 0)
        print(f"Found {market_count} markets")
    except:
        print("Could not parse fetch results")
        return False
    
    if market_count == 0:
        print("No markets found")
        return False
    
    # Detect arbitrage
    print(f"Analyzing for {min_edge}%+ opportunities...")
    result = subprocess.run([
        'python', 'scripts/detect_arbitrage.py',
        'markets.json',
        '--min-edge', str(min_edge),
        '--output', 'arbs.json'
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error detecting arbitrage: {result.stderr}")
        return False
    
    # Parse arbitrage results
    try:
        with open('arbs.json', 'r') as f:
            arb_data = json.load(f)
        
        arb_count = arb_data.get('arbitrage_count', 0)
        arbitrages = arb_data.get('arbitrages', [])
        
        print(f"Found {arb_count} arbitrage opportunities")
        
        if arb_count > 0:
            for arb in arbitrages:
                title = arb.get('title', 'Unknown')
                profit = arb.get('net_profit_pct', 0)
                risk = arb.get('risk_score', 100)
                print(f"  Profit: {title}: {profit:.2f}% (risk: {risk})")
                
                # TODO: Add Telegram alerting here when alert=True
                if alert:
                    print("  Would send Telegram alert here")
        
        return arb_count > 0
        
    except Exception as e:
        print(f"Error parsing arbitrage results: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Polymarket Arbitrage Scanner')
    parser.add_argument('--min-edge', type=float, default=3.0, 
                       help='Minimum edge percentage (default: 3.0)')
    parser.add_argument('--alert', action='store_true',
                       help='Send alerts for opportunities')
    
    args = parser.parse_args()
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    success = run_scan(args.min_edge, args.alert)
    
    if success:
        print("Scan complete - opportunities found!")
    else:
        print("Scan complete - no opportunities")