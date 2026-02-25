#!/usr/bin/env python3
"""Autonomous Profit Taker v2.3 - Modified to exit after closing all positions."""
import os, sys, json, time, asyncio, subprocess, logging
from pathlib import Path
from dotenv import load_dotenv
import httpx

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [PROFITS] %(message)s")
log = logging.getLogger("profits")

WORKSPACE_ROOT = Path(r"C:\Users\vclin_jjufoql\.openclaw\workspace")
POSITIONS_FILE = WORKSPACE_ROOT / "active_positions.json"
JUP_SWAP_PATH = WORKSPACE_ROOT / "skills" / "solana-skills" / "scripts" / "jup_swap.py"

# PROTOCOL: 80/20 Moonbag
TP_MULT = 1.3
SL_MULT = 0.8
TRAILING_DROP = 0.1
VOL_DECAY_THRESHOLD = 0.5

async def get_current_data(mint, amount):
    try:
        api_key = os.environ["JUPITER_API_KEY"]
        order_url = f"https://api.jup.ag/ultra/v1/order?inputMint={mint}&outputMint=So11111111111111111111111111111111111111112&amount={amount}"
        dex_url = f"https://api.dexscreener.com/latest/dex/tokens/{mint}"
        async with httpx.AsyncClient(timeout=10) as client:
            order_resp = await client.get(order_url, headers={"x-api-key": api_key})
            dex_resp = await client.get(dex_url)
            val, vol = 0, 0
            if order_resp.status_code == 200:
                val = int(order_resp.json().get("outAmount", 0)) / 1e9
            if dex_resp.status_code == 200:
                pairs = dex_resp.json().get("pairs", [])
                if pairs:
                    pairs.sort(key=lambda x: float(x.get("liquidity", {}).get("usd", 0)), reverse=True)
                    vol = float(pairs[0].get("volume", {}).get("h1", 0))
            return val, vol
    except: pass
    return 0, 0

def execute_exit(mint, percent, type_label):
    log.info(f"🚨 {type_label} TRIGGERED FOR {mint}. Selling {percent}%...")
    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        cmd = [sys.executable, str(JUP_SWAP_PATH), "sell", mint, str(percent)]
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        data = json.loads(result.stdout)
        if data.get("status") == "Success":
            log.info(f"✅ Exit successful: {data.get('signature')}")
            return True
    except Exception as e:
        log.error(f"Exit failed: {e}")
    return False

async def loop():
    log.info("Profit Taker v2.3 [EXIT_MODE] ACTIVE.")
    while True:
        try:
            if not POSITIONS_FILE.exists():
                log.info("No positions file. Exiting.")
                break
            
            with open(POSITIONS_FILE, "r") as f: positions = json.load(f)
            
            if not positions:
                log.info("No active positions. Task complete. Exiting.")
                break
                
            updated = False
            to_remove = []

            for mint, data in positions.items():
                curr_val, curr_vol = await get_current_data(mint, data["tokens_bought"])
                if curr_val == 0: continue
                
                roi = curr_val / data["entry_sol"]
                peak_roi = data.get("peak_roi", roi)
                
                if roi > peak_roi:
                    positions[mint]["peak_roi"] = roi
                    peak_roi = roi
                    updated = True

                log.info(f"Tracking {data.get('ticker', mint[:6])}: ROI {roi:.2f}x (Peak: {peak_roi:.2f}x) | Vol: ${curr_vol:,.0f}")

                if not data.get("sold_initial"):
                    if peak_roi >= TP_MULT and (peak_roi - roi) >= TRAILING_DROP:
                        if execute_exit(mint, 80, "TRAILING PROFIT"):
                            positions[mint]["sold_initial"] = True
                            updated = True
                    elif roi >= (TP_MULT + 1.0): 
                        if execute_exit(mint, 80, "HARD TAKE PROFIT"):
                            positions[mint]["sold_initial"] = True
                            updated = True
                    elif roi <= SL_MULT:
                        if execute_exit(mint, 100, "STOP LOSS"):
                            to_remove.append(mint)
                            updated = True
                else:
                    if roi > 5.0:
                        if execute_exit(mint, 50, "MOONBAG PROFIT TAKE"):
                            updated = True
                    elif curr_vol < 1000:
                        if execute_exit(mint, 100, "MOONBAG DUST OUT"):
                            to_remove.append(mint)
                            updated = True

                positions[mint]["prev_vol"] = curr_vol
                updated = True

            for m in to_remove:
                if m in positions: del positions[m]
            if updated:
                with open(POSITIONS_FILE, "w") as f: json.dump(positions, f)

            await asyncio.sleep(30)
        except Exception as e:
            log.error(f"Loop error: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(loop())
