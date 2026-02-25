#!/usr/bin/env python3
"""Training Script - Analyzing Top Solana Runners to Refine Sniper Filters."""
import httpx, json, time, os, sys
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def get_top_runners():
    print("Fetching current Solana market leaders...")
    url = "https://api.dexscreener.com/latest/dex/search?q=solana"
    try:
        resp = httpx.get(url, timeout=15)
        if resp.status_code == 200:
            pairs = resp.json().get('pairs', [])
            # Filter for Solana + Recent Breakouts (>100% 24h gain)
            runners = [p for p in pairs if p.get('chainId') == 'solana' and float(p.get('priceChange', {}).get('h24', 0)) > 100]
            runners.sort(key=lambda x: float(x.get('volume', {}).get('h24', 0)), reverse=True)
            return runners[:20]
    except Exception as e:
        print(f"Error fetching runners: {e}")
    return []

def analyze_profile(runner):
    mc = float(runner.get('marketCap', 0))
    vol_24h = float(runner.get('volume', {}).get('h24', 0))
    liq = float(runner.get('liquidity', {}).get('usd', 0))
    
    eff_score = vol_24h / liq if liq > 0 else 0
    
    return {
        "ticker": runner.get('baseToken', {}).get('symbol'),
        "mc": mc,
        "vol_liq_ratio": round(eff_score, 2),
        "price_change_h24": runner.get('priceChange', {}).get('h24'),
        "boosts": runner.get('boosts', {}).get('active', 0)
    }

def main():
    runners = get_top_runners()
    profiles = [analyze_profile(r) for r in runners]
    
    print("\n--- RUNNER PROFILES ---")
    for p in profiles:
        print(f"{p['ticker']}: MC ${p['mc']:,.0f} | Vol/Liq: {p['vol_liq_ratio']} | Gain: {p['price_change_h24']}% | Boosts: {p['boosts']}")

    avg_ratio = sum(p['vol_liq_ratio'] for p in profiles) / len(profiles) if profiles else 3.0
    
    print("\n--- REFINED FILTER RECOMMENDATION ---")
    print(f"1. VOL_LIQ_MAX: {min(avg_ratio * 1.5, 10.0)}")
    print(f"2. MIN_BOOSTS: 10")
    print(f"3. SUSTAINED_VOL_H1: > $25,000")

    kb_path = Path("knowledge/trading_intelligence.json")
    kb_path.parent.mkdir(exist_ok=True)
    with open(kb_path, "w") as f:
        json.dump(profiles, f, indent=2)
    print(f"\nIntelligence saved to {kb_path}")

if __name__ == "__main__":
    main()
