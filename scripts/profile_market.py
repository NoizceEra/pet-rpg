#!/usr/bin/env python3
"""Refined Sniper Logic - Signal Mode & Volatility Profiling."""
import httpx, json, time, os, sys
from pathlib import Path
from anti_manipulation import AntiManipulation

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# REFINED CONSTANTS FROM TODAY'S TRAINING
VOL_LIQ_MAX = 4.5
MIN_BOOSTS = 10
SUSTAINED_VOL_H1 = 25000

def profile_market(mint):
    """Deep profile of a single mint to distinguish real accumulation from wash."""
    # Run Anti-Manipulation Layer First
    am = AntiManipulation(mint)
    mani_report = am.analyze()
    
    if mani_report.get("status") == "error": return None
    if mani_report.get("manipulation_score", 0) > 60:
        print(f"🚨 SKIPPING {mani_report['ticker']}: High Manipulation Score ({mani_report['manipulation_score']})")
        return None

    url = f"https://api.dexscreener.com/latest/dex/tokens/{mint}"
    try:
        resp = httpx.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            pairs = [p for p in data.get('pairs', []) if p.get('chainId') == 'solana']
            if not pairs: return None
            
            pairs.sort(key=lambda x: float(x.get('liquidity', {}).get('usd', 0)), reverse=True)
            p = pairs[0]
            
            vol_24h = float(p.get('volume', {}).get('h24', 0))
            liq = float(p.get('liquidity', {}).get('usd', 0))
            vol_h1 = float(p.get('volume', {}).get('h1', 0))
            
            ratio = vol_24h / liq if liq > 0 else 0
            boosts = p.get('boosts', {}).get('active', 0)
            
            # SCORING LOGIC
            score = 0
            if ratio < VOL_LIQ_MAX: score += 30 
            if boosts >= MIN_BOOSTS: score += 30 
            if vol_h1 >= SUSTAINED_VOL_H1: score += 40 
            
            return {
                "ticker": p.get('baseToken', {}).get('symbol'),
                "vulture_score": score,
                "manipulation_report": mani_report,
                "ratio": round(ratio, 2),
                "vol_h1": vol_h1,
                "boosts": boosts
            }
    except: pass
    return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        res = profile_market(sys.argv[1])
        if res:
            print(json.dumps(res, indent=2))
    else:
        print("Usage: python profile_market.py <MINT_ADDRESS>")
