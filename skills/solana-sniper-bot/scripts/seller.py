import os, json, time, asyncio, logging
from pathlib import Path
from dotenv import load_dotenv
import httpx

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [SELLER] %(message)s")
log = logging.getLogger("seller")

# JUPITER CONFIG
JUPITER_IP = "3.160.107.43"
JUPITER_HOST = "api.jup.ag"
JUPITER_QUOTE = f"https://{JUPITER_IP}/v6/quote"
JUPITER_SWAP = f"https://{JUPITER_IP}/v6/swap"

SOL_MINT = "So11111111111111111111111111111111111111112"
PRIVATE_KEY = os.environ["SOLANA_PRIVATE_KEY"]
RPC_URL = os.getenv("RPC_URL", "https://api.mainnet-beta.solana.com")

WORKSPACE_ROOT = Path(r"C:\Users\vclin_jjufoql\.openclaw\workspace")
TRADES_LOG = WORKSPACE_ROOT / "trades.jsonl"

TAKE_PROFIT = 1.5
STOP_LOSS = 0.8

async def get_price(mint):
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(f"https://api.jup.ag/price/v2?ids={mint}")
            data = resp.json()
            return float(data['data'][mint]['price'])
        except:
            return None

async def execute_sell(mint, amount_token):
    # This requires knowing token balance. Simplified for now: just sell all.
    # Logic to fetch balance and execute swap via Jupiter.
    # For now, let's just log the 'Signal' until we can fetch exact balances reliably.
    log.info(f"!!! SELL SIGNAL TRIGGERED FOR {mint} !!!")

async def monitor_positions():
    log.info("Starting Position Monitor/Seller...")
    while True:
        try:
            if not TRADES_LOG.exists():
                await asyncio.sleep(60); continue
            
            # Read trades
            active_mints = []
            with open(TRADES_LOG, "r") as f:
                for line in f:
                    trade = json.loads(line)
                    # For simplicity, treat all trades as active if not sold
                    active_mints.append(trade)

            for trade in active_mints:
                mint = trade['mint']
                # entry_price isn't in log yet. Sniper needs to log it.
                # Skipping actual price check until log has entry_price.
                pass

        except Exception as e:
            log.error(f"Seller error: {e}")
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(monitor_positions())
