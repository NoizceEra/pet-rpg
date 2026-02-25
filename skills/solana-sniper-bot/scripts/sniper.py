#!/usr/bin/env python3
"""Solana Token Sniper — Overclocked Vulture v3.3 (Dip Buying Mode)."""
import os, sys, json, time, logging, asyncio, subprocess
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
import httpx

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("sniper")

WORKSPACE_ROOT = Path(r"C:\Users\vclin_jjufoql\.openclaw\workspace")
PRIVATE_KEY = os.environ.get("SOLANA_PRIVATE_KEY")
LLM_API_KEY = os.environ.get("LLM_API_KEY")
RPC_URL = os.getenv("RPC_URL_PUBLIC", "https://api.mainnet-beta.solana.com")

# CONFIG
CONFIG_FILE = WORKSPACE_ROOT / "trading_config.json"
TRADES_LOG = WORKSPACE_ROOT / "trades.jsonl"
POSITIONS_FILE = WORKSPACE_ROOT / "active_positions.json"
WATCHLIST_FILE = WORKSPACE_ROOT / "watchlist.json"
JUP_SWAP_PATH = WORKSPACE_ROOT / "skills" / "solana-skills" / "scripts" / "jup_swap.py"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

async def get_wallet_balance() -> float:
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(RPC_URL, json={"jsonrpc": "2.0", "id": 1, "method": "getBalance", "params": ["BKVU94WsjhfwPHMKLPXQFc4s9n9T3GbXtFUUxY9W6uMw"]})
            return resp.json().get("result", {}).get("value", 0) / 1e9
        except: return 0.1

async def get_token_metadata(mint):
    """Fetch Name, Symbol, MC, Liq from DexScreener."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"https://api.dexscreener.com/latest/dex/tokens/{mint}")
            if resp.status_code == 200:
                data = resp.json()
                pairs = data.get("pairs", [])
                if pairs:
                    pairs.sort(key=lambda x: float(x.get("liquidity", {}).get("usd", 0)), reverse=True)
                    p = pairs[0]
                    return {
                        "name": p.get("baseToken", {}).get("name", "Unknown"),
                        "ticker": p.get("baseToken", {}).get("symbol", "???"),
                        "mc": float(p.get("marketCap", 0)),
                        "liq": float(p.get("liquidity", {}).get("usd", 0)),
                        "volume_h1": float(p.get("volume", {}).get("h1", 0)),
                        "dex": p.get("dexId", "unknown")
                    }
    except Exception as e:
        log.error(f"Metadata fetch error for {mint}: {e}")
    return {"name": "Unknown", "ticker": "???", "mc": 0, "liq": 0, "volume_h1": 0, "dex": "unknown"}

async def llm_evaluate(mint, liq):
    if not LLM_API_KEY: return 0.5
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            prompt = f"Assess risk for Solana mint {mint} with ${liq} liquidity. Key Meta Keywords: Agentic Autonomy, Social Velocity, CTO Legitimacy, IP Hybridization, Defeatist Irony. Reply 0.0-1.0 only (0=Safe, 1=Rug)."
            resp = await client.post("https://api.anthropic.com/v1/messages",
                headers={"x-api-key": LLM_API_KEY, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
                json={"model": "claude-3-haiku-20240307", "max_tokens": 10, "messages": [{"role": "user", "content": prompt}]})
            return float(resp.json()["content"][0]["text"].split()[0].strip(".,"))
        except: return 0.5

async def execute_swap(mint, amount_sol):
    log.info(f"🔥 EXECUTING BUY: {mint} for {amount_sol} SOL")
    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        cmd = [sys.executable, str(JUP_SWAP_PATH), "swap", "SOL", mint, str(amount_sol)]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            data = json.loads(stdout.decode().strip())
            if data.get("status") == "Success":
                return data
        else:
            log.error(f"Swap failed (code {process.returncode}): {stderr.decode().strip()}")
        return None
    except Exception as e:
        log.error(f"Swap failed: {e}")
        return None

async def monitor():
    log.info("Vulture Sniper v3.3 (Dip Buying Mode) ACTIVE.")
    seen = set()
    
    while True:
        try:
            cfg = load_config()
            s_cfg = cfg["sniper"]
            entry_mode = s_cfg.get("entry_mode", "pump")
            
            async with httpx.AsyncClient(timeout=10) as client:
                # 1. SCOUTING NEW CANDIDATES
                resp = await client.get("https://api.dexscreener.com/token-boosts/latest/v1")
                if resp.status_code == 200:
                    candidates = [p for p in resp.json() if p.get("chainId") == "solana"]
                    for p in candidates:
                        m = p.get("tokenAddress")
                        if m and m not in seen:
                            seen.add(m)
                            meta = await get_token_metadata(m)
                            
                            if meta['volume_h1'] < s_cfg["min_volume_h1"]:
                                continue
                            
                            risk_val = await llm_evaluate(m, meta['liq'])
                            if risk_val * 100 < s_cfg["risk_threshold"]:
                                if entry_mode == "pump":
                                    # OLD LOGIC: BUY IMMEDIATELY
                                    await buy_token(m, meta, s_cfg, cfg)
                                else:
                                    # NEW LOGIC: WATCHLIST
                                    log.info(f"👀 Watchlisting {meta['ticker']} for dip...")
                                    watchlist = {}
                                    if WATCHLIST_FILE.exists():
                                        with open(WATCHLIST_FILE, "r") as f: watchlist = json.load(f)
                                    
                                    watchlist[m] = {
                                        "ticker": meta["ticker"],
                                        "peak_mc": meta["mc"],
                                        "timestamp": time.time(),
                                        "last_mc": meta["mc"]
                                    }
                                    with open(WATCHLIST_FILE, "w") as f: json.dump(watchlist, f, indent=4)

                # 2. MONITOR WATCHLIST FOR DIPS
                if entry_mode == "dip" and WATCHLIST_FILE.exists():
                    with open(WATCHLIST_FILE, "r") as f: watchlist = json.load(f)
                    
                    to_remove = []
                    for m, data in watchlist.items():
                        meta = await get_token_metadata(m)
                        if meta['mc'] > data['peak_mc']:
                            watchlist[m]['peak_mc'] = meta['mc']
                        
                        watchlist[m]['last_mc'] = meta['mc']
                        
                        # Check Dip Threshold (e.g., 40% drop from peak)
                        dip_threshold = s_cfg.get("dip_buy_threshold", 0.40)
                        if data['peak_mc'] > 0:
                            drop = (data['peak_mc'] - meta['mc']) / data['peak_mc']
                            log.info(f"[{data['ticker']}] Dip: {drop:.0%} (Target: {dip_threshold:.0%}) | MC: ${meta['mc']:,.0f}")
                            
                            if drop >= dip_threshold and meta['volume_h1'] >= s_cfg["min_volume_h1"]:
                                log.info(f"📉 DIP BUY TRIGGERED for {data['ticker']}!")
                                if await buy_token(m, meta, s_cfg, cfg):
                                    to_remove.append(m)
                        
                        # Remove if older than 4 hours without hitting dip
                        if time.time() - data['timestamp'] > 14400:
                            log.info(f"Removing {data['ticker']} from watchlist (expired)")
                            to_remove.append(m)
                            
                    for m in to_remove:
                        if m in watchlist: del watchlist[m]
                    
                    with open(WATCHLIST_FILE, "w") as f: json.dump(watchlist, f, indent=4)
                
            await asyncio.sleep(s_cfg.get("scout_interval", 15))
            
        except Exception as e:
            log.error(f"Monitor error: {e}")
            await asyncio.sleep(5)

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

async def buy_token(m, meta, s_cfg, cfg):
    balance = await get_wallet_balance()
    floor = cfg["global"]["safety_floor_sol"]
    if balance < floor:
        log.warning(f"Safety Floor reached ({balance} < {floor}). Cannot buy.")
        return False
        
    buy_amount = round(balance * s_cfg["dynamic_sizing"]["percent_of_balance"], 3)
    if buy_amount > cfg["global"]["max_buy_sol"]:
        buy_amount = cfg["global"]["max_buy_sol"]
        
    swap_res = await execute_swap(m, buy_amount)
    if swap_res:
        log.info(f"✅ BOUGHT {meta['ticker']}")
        
        # Thesis and Exit Strategy Alert
        v_cfg = cfg.get("vulture", {})
        exit_strat = ", ".join([f"{s['roi']}x ({s['sell_percent']}%)" for s in v_cfg.get("exit_stages", [])])
        
        # Determine Thesis based on mode
        entry_mode = s_cfg.get("entry_mode", "pump")
        if entry_mode == "dip":
            thesis = f"Re-entry on significant dip ({s_cfg.get('dip_buy_threshold', 0.40)*100}% correction) with healthy volume (${meta['volume_h1']:,.0f}). LLM Risk Check passed."
        else:
            thesis = f"Momentum capture on {meta['dex']} with strong volume growth. LLM Risk Check passed."

        alert_msg = (
            f"🎯 *New Trade Entered: ${meta['ticker']}*\n\n"
            f"🧠 *Thesis:* {thesis}\n"
            f"📉 *Entry:* {buy_amount} SOL\n"
            f"🚀 *Exit Strategy:* {exit_strat}\n"
            f"🛡️ *Stop Loss:* {v_cfg.get('stop_loss', {}).get('roi_threshold', 0.85)}x"
        )
        add_alert(alert_msg)

        pos = {}
        if POSITIONS_FILE.exists():
            with open(POSITIONS_FILE, "r") as f: pos = json.load(f)
        
        pos[m] = {
            "name": meta["name"],
            "ticker": meta["ticker"],
            "mint": m,
            "entry_sol": buy_amount,
            "tokens_bought": int(swap_res.get("outAmount", 0)),
            "timestamp": time.time(),
            "peak_roi_v3": 1.0,
            "prev_roi": 1.0,
            "stages_hit": [],
            "sold_initial": False
        }
        with open(POSITIONS_FILE, "w") as f: json.dump(pos, f, indent=4)
        return True
    return False

if __name__ == "__main__":
    asyncio.run(monitor())
