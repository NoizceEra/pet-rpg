#!/usr/bin/env python3
"""
Vulture Anti-Manipulation Layer v1.0
Specialized filters to detect wash trading, stop-loss hunting, and shakeouts.
"""
import httpx, json, time, os, sys
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

class AntiManipulation:
    def __init__(self, mint):
        self.mint = mint
        self.url = f"https://api.dexscreener.com/latest/dex/tokens/{mint}"

    def analyze(self):
        try:
            resp = httpx.get(self.url, timeout=10)
            if resp.status_code != 200: return {"status": "error", "message": "API unreachable"}
            
            data = resp.json()
            pairs_raw = data.get('pairs') or []
            pairs = [p for p in pairs_raw if p and p.get('chainId') == 'solana']
            if not pairs: return {"status": "error", "message": "No Solana pairs found"}
            
            p = pairs[0]
            
            # 1. STOP-LOSS HUNT DETECTION (Price Wick Analysis)
            # If price dropped >15% in last 5m but volume is low, it's a shakeout wick.
            price_change = p.get('priceChange') or {}
            change_m5 = float(price_change.get('m5', 0))
            
            # 2. WASH TRADE DETECTION (Vol/Liq Efficiency)
            volume_data = p.get('volume') or {}
            vol_24h = float(volume_data.get('h24', 0))
            liq_data = p.get('liquidity') or {}
            liq = float(liq_data.get('usd', 0))
            eff_ratio = vol_24h / liq if liq > 100 else 0
            
            # 3. SOCIAL DEPTH (Boosts per Million MC)
            boosts_data = p.get('boosts') or {}
            boosts = boosts_data.get('active', 0)
            mc = float(p.get('marketCap') or p.get('fdv') or 1)
            social_density = (boosts / mc) * 1_000_000 if mc > 0 else 0

            # 4. SKEWNESS (Buy/Sell Ratio)
            txns_data = p.get('txns') or {}
            txns_h1 = txns_data.get('h1') or {}
            buys = txns_h1.get('buys', 0)
            sells = txns_h1.get('sells', 0)
            bs_ratio = buys / (sells + 1)

            analysis = {
                "ticker": p.get('baseToken', {}).get('symbol'),
                "is_shakeout": change_m5 < -15 and bs_ratio > 2, # Sharp dip but buyers entering
                "is_wash_trade": eff_ratio > 10, # Suspiciously high volume relative to liq
                "social_conviction": boosts >= 10,
                "manipulation_score": 0, # 0 = Organic, 100 = High Sus
                "metrics": {
                    "eff_ratio": round(eff_ratio, 2),
                    "bs_ratio": round(bs_ratio, 2),
                    "social_density": round(social_density, 2)
                }
            }

            # Scoring logic
            if analysis["is_wash_trade"]: analysis["manipulation_score"] += 50
            if bs_ratio < 0.5: analysis["manipulation_score"] += 30 # Selling pressure
            if not analysis["social_conviction"]: analysis["manipulation_score"] += 20

            return analysis

        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        am = AntiManipulation(sys.argv[1])
        print(json.dumps(am.analyze(), indent=2))
    else:
        print("Usage: python anti_manipulation.py <MINT>")
