#!/usr/bin/env python3
"""
Vulture Engine v3.0 - Precise Profit Taking & Dip Buying
Implements staged micro-sells and re-accumulation (buy the dip).
"""
import os, sys, json, time, asyncio, subprocess, logging, base64, ssl
from pathlib import Path
from dotenv import load_dotenv
import httpx
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [VULTURE-v3] %(message)s")
log = logging.getLogger("vulture")

# PATHS
WORKSPACE_ROOT = Path(r"C:\Users\vclin_jjufoql\.openclaw\workspace")
POSITIONS_FILE = WORKSPACE_ROOT / "active_positions.json"
WALLETS_FILE = WORKSPACE_ROOT / "moltwars-wallet.json" # Expansion ready

# CONFIG LOAD
CONFIG_FILE = WORKSPACE_ROOT / "trading_config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

cfg = load_config()
v_cfg = cfg["vulture"]

# STRATEGY: MICRO-SELLS
EXIT_STAGES = v_cfg["exit_stages"]

# STRATEGY: STOP LOSS
STOP_LOSS_THRESHOLD = v_cfg["stop_loss"]["vol_decay_threshold"]
ROI_STOP_LOSS = v_cfg["stop_loss"]["roi_threshold"]

# STRATEGY: SPIKE SHAVING
SPIKE_THRESHOLD = v_cfg["spike_shaving"]["jump_threshold"]
SPIKE_SELL_PERCENT = v_cfg["spike_shaving"]["sell_percent"]

# STRATEGY: DIP BUYING (LEGACY - NOT IN CONFIG YET)
DIP_THRESHOLD = 0.40
DIP_VOL_MIN = 50000
DIP_BUY_AMOUNT = 0.0

# RPC & JUPITER
RPC_URL = "https://api.mainnet-beta.solana.com"
JUP_IP = "108.162.192.59"
JUP_HOST = "quote-api.jup.ag"
SOL_MINT = "So11111111111111111111111111111111111111112"

ALERTS_FILE = WORKSPACE_ROOT / "solana-alerts.json"

def add_alert(alert_text):
    alerts = []
    if ALERTS_FILE.exists():
        try:
            with open(ALERTS_FILE, "r") as f:
                alerts = json.load(f)
        except: alerts = []
    
    alerts.append({
        "timestamp": time.time(),
        "message": alert_text
    })
    
    with open(ALERTS_FILE, "w") as f:
        json.dump(alerts, f, indent=4)

async def get_market_data(mint, amount_tokens):
    """Fetch current value in SOL and 1h volume."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        
        async with httpx.AsyncClient(timeout=5) as client:
            # DexScreener for Volume AND Price
            d_url = f"https://api.dexscreener.com/latest/dex/tokens/{mint}"
            d_resp = await client.get(d_url)
            val, vol = 0, 0
            if d_resp.status_code == 200:
                pairs = d_resp.json().get("pairs", [])
                if pairs:
                    price_native = float(pairs[0].get("priceNative", 0))
                    vol = float(pairs[0].get("volume", {}).get("h1", 0))
                    if amount_tokens > 0:
                        val = (amount_tokens / 1e6) * price_native # Pump tokens are 6 decimals usually
                    else:
                        val = price_native * 1e3 # placeholder
            
            return val, vol
    except Exception as e:
        log.error(f"Data fetch error for {mint}: {e}")
    return 0, 0

async def execute_trade(action, mint, amount_val, is_sol=True):
    """Execute Buy (SOL) or Sell (%) using jup_swap.py."""
    log.info(f"🚨 EXECUTION: {action} {mint} | Value/Percent: {amount_val}")
    
    JUP_SWAP_PATH = WORKSPACE_ROOT / "skills" / "solana-skills" / "scripts" / "jup_swap.py"
    
    try:
        cmd = [sys.executable, str(JUP_SWAP_PATH)]
        if action == "BUY":
            cmd += ["swap", "SOL", mint, str(amount_val)]
        else: # SELL
            # For SELL, amount_val is now treated as a percentage (1-100)
            cmd += ["sell", mint, str(amount_val)]

        # Run as async subprocess to prevent blocking
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            data = json.loads(stdout.decode().strip())
            if "error" not in data:
                log.info(f"✅ Trade Success: {data}")
                return True
            else:
                log.error(f"❌ Trade Error: {data['error']}")
        else:
            log.error(f"❌ Trade Execution Failed (code {process.returncode}): {stderr.decode().strip()}")
    except Exception as e:
        log.error(f"Trade execution failed: {e}")
    return False

async def main_loop():
    log.info("Vulture Engine v3.0 STARTING...")
    
    while True:
        try:
            if not POSITIONS_FILE.exists():
                await asyncio.sleep(60); continue
                
            with open(POSITIONS_FILE, "r") as f:
                positions = json.load(f)
            
            updated = False
            
            for mint, data in positions.items():
                tokens = data.get("tokens_bought", 0)
                if tokens <= 0: continue
                
                curr_sol_val, curr_vol_h1 = await get_market_data(mint, tokens)
                if curr_sol_val == 0: continue
                
                roi = curr_sol_val / data["entry_sol"]
                peak_roi = data.get("peak_roi_v3", roi)
                prev_roi = data.get("prev_roi", roi)
                stages_hit = data.get("stages_hit", [])
                
                # Update Peak & Prev
                if roi > peak_roi:
                    positions[mint]["peak_roi_v3"] = roi
                    peak_roi = roi
                positions[mint]["prev_roi"] = roi
                updated = True
                
                log.info(f"[{data.get('ticker', '???')}] ROI: {roi:.2f}x | Peak: {peak_roi:.2f}x | Vol: ${curr_vol_h1:,.0f}")
                
                # 1. SPIKE SHAVING LOGIC
                # If ROI jumps > threshold in one loop (5s), shave percent of REMAINING immediately
                if prev_roi > 0 and (roi - prev_roi) / prev_roi >= SPIKE_THRESHOLD:
                    log.info(f"⚡ SPIKE DETECTED: {mint} jumped {(roi-prev_roi)/prev_roi:.0%} in loop. Shaving {SPIKE_SELL_PERCENT}%...")
                    if await execute_trade("SELL", mint, SPIKE_SELL_PERCENT, is_sol=False): 
                        add_alert(f"⚡ *Spike Shave:* Shaved {SPIKE_SELL_PERCENT}% of ${data.get('ticker', '???')} after a {(roi-prev_roi)/prev_roi:.0%} jump.")
                        positions[mint]["tokens_bought"] = tokens * (1 - (SPIKE_SELL_PERCENT/100))
                        updated = True

                # 2. STOP LOSS LOGIC (NEW)
                if roi <= ROI_STOP_LOSS:
                    log.warning(f"🚨 STOP LOSS TRIGGERED: {mint} ROI at {roi:.2f}x (Threshold: {ROI_STOP_LOSS}x). Liquidating...")
                    if await execute_trade("SELL", mint, 100, is_sol=False): # Sell 100%
                        add_alert(f"🚨 *Stop Loss:* Liquidated ${data.get('ticker', '???')} at {roi:.2f}x ROI.")
                        positions[mint]["tokens_bought"] = 0
                        updated = True
                        continue

                # 3. MICRO-SELL LOGIC
                for i, stage in enumerate(EXIT_STAGES):
                    if i not in stages_hit and roi >= stage["roi"]:
                        log.info(f"🎯 Milestone reached: {stage['label']} ({stage['roi']}x)")
                        if await execute_trade("SELL", mint, stage["sell_percent"], is_sol=False): # Pass percent
                            add_alert(f"🎯 *Take Profit:* {stage['label']} reached for ${data.get('ticker', '???')} ({roi:.2f}x). Sold {stage['sell_percent']}% of remainder.")
                            positions[mint]["stages_hit"] = stages_hit + [i]
                            # Update tokens remaining (approximate for tracking)
                            positions[mint]["tokens_bought"] = tokens * (1 - (stage["sell_percent"]/100))
                            updated = True
                            break # One stage per loop to avoid double selling
                
                # 2. DIP BUYING LOGIC
                # Only buy dip if we've already taken some profit (stage 0 hit)
                if stages_hit and (peak_roi - roi) / peak_roi >= DIP_THRESHOLD:
                    if curr_vol_h1 >= DIP_VOL_MIN:
                        last_dip_buy = data.get("last_dip_buy_time", 0)
                        if time.time() - last_dip_buy > 3600: # Max once per hour
                            log.info(f"📉 DIP DETECTED: {mint} dropped {(peak_roi-roi)/peak_roi:.0%} from peak. Re-accumulating...")
                            if await execute_trade("BUY", mint, DIP_BUY_AMOUNT, is_sol=True):
                                add_alert(f"📉 *Dip Re-entry:* Bought more ${data.get('ticker', '???')} after {(peak_roi-roi)/peak_roi:.0%} drop from peak.")
                                positions[mint]["last_dip_buy_time"] = time.time()
                                # Note: In a real scenario, we'd update tokens_bought from the tx result
                                updated = True

            if updated:
                with open(POSITIONS_FILE, "w") as f:
                    json.dump(positions, f, indent=4)
                    
            await asyncio.sleep(v_cfg.get("loop_interval_seconds", 5)) # Configurable interval
            
        except Exception as e:
            log.error(f"Loop error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main_loop())
