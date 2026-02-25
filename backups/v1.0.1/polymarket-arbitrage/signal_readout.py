import json
import os
from pathlib import Path
from datetime import datetime

def show_signals():
    workspace = Path(r"C:\Users\vclin_jjufoql\.openclaw\workspace\polymarket-arbitrage")
    forensics = workspace / "forensics"
    
    files = list(forensics.glob("trade_*.json"))
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    print("\n" + "="*60)
    print(" PINCHIE'S ACTIVE TRADING SIGNALS (PAPER MODE)")
    print("="*60)
    
    if not files:
        print(" No signals detected yet. Engine is scanning...")
    else:
        for f in files[:10]: # Last 10 signals
            try:
                with open(f, "r", encoding='utf-8') as tf:
                    data = json.load(tf)
                
                t = data['timestamp'].split('T')[1][:8]
                m = data['market'][:35]
                s = data['strategy'].replace('_', ' ').upper()
                p = data['details'].get('profit', 0) if 'profit' in data['details'] else data['details'].get('price', 0)*100
                
                print(f" [{t}] {s:<12} | {m:<35}... | {p:>5.1f}%")
            except:
                pass
                
    print("="*60)
    print(" Exit Strategy: All positions held until market resolution.")
    print("="*60)

if __name__ == "__main__":
    show_signals()
