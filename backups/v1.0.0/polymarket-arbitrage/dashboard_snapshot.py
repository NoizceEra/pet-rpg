import json
import os
import time
from datetime import datetime
from pathlib import Path

def get_snapshot():
    workspace = Path(r"C:\Users\vclin_jjufoql\.openclaw\workspace\polymarket-arbitrage")
    forensics = workspace / "forensics"
    
    # 1. Engine Status
    engine_state = {}
    state_file = forensics / "engine_state.json"
    if state_file.exists():
        try:
            with open(state_file, "rb") as f:
                content = f.read().decode('utf-16')
                engine_state = json.loads(content)
        except:
            pass
            
    # 2. Recent Trades
    trades = []
    trade_files = list(forensics.glob("trade_*.json"))
    trade_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    for tf in trade_files[:5]:
        try:
            with open(tf, "r") as f:
                trades.append(json.load(f))
        except:
            pass
            
    # 3. Latest Scan Results
    latest_arbs = []
    arbs_file = workspace / "polymarket_data" / "arbs.json"
    if arbs_file.exists():
        try:
            with open(arbs_file, "r") as f:
                data = json.load(f)
                latest_arbs = data.get("arbitrages", [])
        except:
            pass

    print("\n" + "="*50)
    print(" PINCHIE'S AUTONOMOUS ENGINE DASHBOARD")
    print("="*50)
    print(f" Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f" Strategy: {engine_state.get('strategy', 'Sharbel Forensic Engine')}")
    print(f" Engine Status: {engine_state.get('status', 'Scanning...')}")
    print("="*50)
    
    print("\nLATEST SCAN RESULTS:")
    if latest_arbs:
        for arb in latest_arbs[:5]:
            print(f" - [{arb['net_profit_pct']:.2f}%] {arb['title'][:40]}...")
    else:
        print(" - No active arbitrage opportunities found in last scan.")
        
    print("\nRECENT ACTIVITY (Forensics):")
    if trades:
        for trade in trades:
            print(f" - {trade['timestamp'].split('T')[1][:8]} | {trade['market'][:35]}... | {trade['status']}")
    else:
        print(" - No trades executed yet. Standing by.")
        
    print("\n" + "="*50)

if __name__ == "__main__":
    get_snapshot()
