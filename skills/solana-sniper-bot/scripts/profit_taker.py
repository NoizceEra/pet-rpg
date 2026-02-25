import os, json, time, asyncio, logging, subprocess, sys
from pathlib import Path
from dotenv import load_dotenv
import httpx

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [PROFITS] %(message)s")
log = logging.getLogger("profit_taker")

WORKSPACE_ROOT = Path(r"C:\Users\vclin_jjufoql\.openclaw\workspace")
JUP_SWAP_PATH = WORKSPACE_ROOT / "skills" / "solana-skills" / "scripts" / "jup_swap.py"
POSITIONS_FILE = WORKSPACE_ROOT / "active_positions.json"

# PROTOCOL: 80/20 Moonbag
TAKE_PROFIT_MULT = 1.3
STOP_LOSS_MULT = 0.8
SELL_PERCENT = 0.8 # Sell 80% on TP

async def get_prices(mints):
    ids = ",".join(mints)
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(f"https://api.jup.ag/price/v2?ids={ids}")
            return resp.json().get('data', {})
        except:
            return {}

def execute_sell(mint, amount_percent):
    """Executes sell via jup_swap script."""
    log.info(f"🔥 EXECUTING PROFIT TAKE: {mint} ({amount_percent*100}%)")
    # To sell a percentage, we first need to fetch the balance.
    # jup_swap.py needs to be updated to support 'sell' command or handle percentage.
    # For now, I'll update jup_swap.py to handle a 'sell' command that fetches balance.
    pass

async def run():
    log.info("Profit Taker v1.0 ACTIVE. Prioritizing exits.")
    
    # Initialize positions if not exist (using provided data)
    if not POSITIONS_FILE.exists():
        initial_data = {
            "2zDUMheEbHB9e42zS2Qn8kve8ET6bR5m1A87qd7Spump": {"ticker": "Trilly", "entry_sol": 0.079, "sold_initial": False},
            "8AX9SQ8kGUBwo2nThJ98i3Eus8aAFCDzbch2KWsepump": {"ticker": "GiraffeGPT", "entry_sol": 0.039, "sold_initial": False},
            "7qMManxJoj8nLUvRwgQe3D9KZf6iCvVLcv7Vm5Hkpump": {"ticker": "ROHUN", "entry_sol": 0.05, "sold_initial": False}
        }
        with open(POSITIONS_FILE, "w") as f:
            json.dump(initial_data, f)

    while True:
        try:
            with open(POSITIONS_FILE, "r") as f:
                positions = json.load(f)

            if not positions:
                await asyncio.sleep(30); continue

            mints = list(positions.keys())
            prices = await get_prices(mints)

            for mint, data in positions.items():
                if mint not in prices or not prices[mint]:
                    continue
                
                # Logic to determine ROI based on price change
                # Simplified: Fetching quote for current balance to SOL
                # But since we want to be fast, we use the price API.
                
                # Check price action
                # Need to store entry price to use Price API effectively
                pass

            await asyncio.sleep(15)
        except Exception as e:
            log.error(f"Profit Taker error: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(run())
