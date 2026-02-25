#!/usr/bin/env python3
"""
Telegram Trade Monitor - Interactive Module for Team Pinchie
Generates a status card with buttons for Solana tokens.
"""
import os, sys, json, httpx, asyncio
from pathlib import Path

# Paths
WORKSPACE_ROOT = Path(r"C:\Users\vclin_jjufoql\.openclaw\workspace")
POSITIONS_FILE = WORKSPACE_ROOT / "active_positions.json"

async def get_token_data(mint):
    """Fetch live data from DexScreener."""
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{mint}"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                pairs = data.get("pairs", [])
                if pairs:
                    # Sort by liquidity
                    pairs.sort(key=lambda x: float(x.get("liquidity", {}).get("usd", 0)), reverse=True)
                    return pairs[0]
    except Exception as e:
        print(f"Error fetching data: {e}")
    return None

async def generate_monitor_card(mint):
    """Generate the formatted text and buttons for a token."""
    # 1. Get position info from local state
    if not POSITIONS_FILE.exists():
        return "Error: No active positions found.", []
        
    with open(POSITIONS_FILE, "r") as f:
        positions = json.load(f)
    
    pos = positions.get(mint)
    if not pos:
        return f"Error: Position for {mint} not found.", []

    # 2. Get live market data
    market = await get_token_data(mint)
    if not market:
        return f"Error: Could not fetch market data for {mint}.", []

    # 3. Calculate metrics
    name = market.get("baseToken", {}).get("name", pos.get("name", "Unknown"))
    ticker = market.get("baseToken", {}).get("symbol", pos.get("ticker", "???"))
    mc = float(market.get("fdv", 0))
    vol_h1 = float(market.get("volume", {}).get("h1", 0))
    price_native = float(market.get("priceNative", 0))
    
    holdings = pos.get("tokens_bought", 0)
    entry_sol = pos.get("entry_sol", 0)
    
    # Calculate current value based on DexScreener price
    price_sol = float(market.get("priceNative", 0))
    # holdings are stored as raw units (usually 6 decimals for pump tokens)
    curr_value_sol = (holdings / 1e6) * price_sol
    roi = curr_value_sol / entry_sol if entry_sol > 0 else 0

    message = (
        f"🦀 *Trade Monitor: {name} (${ticker})*\n\n"
        f"📑 *CA:* `{mint}`\n"
        f"📊 *MC:* ${mc:,.0f}\n"
        f"💧 *Vol (1h):* ${vol_h1:,.0f}\n\n"
        f"💰 *Holdings:* {holdings:,.0f} units\n"
        f"📉 *Avg Entry:* {entry_sol:.4f} SOL\n"
        f"📈 *Current Value:* {curr_value_sol:.4f} SOL ({roi:.2f}x)\n\n"
        f"🛠️ *Sell Configuration:*"
    )

    buttons = [
        [
            {"text": "🔄 Refresh", "callback_data": f"monitor:refresh:{mint}"}
        ],
        [
            {"text": "25%", "callback_data": f"monitor:sell:25:{mint}"},
            {"text": "50%", "callback_data": f"monitor:sell:50:{mint}"},
            {"text": "100%", "callback_data": f"monitor:sell:100:{mint}"}
        ]
    ]

    return message, buttons

async def main():
    if len(sys.argv) < 2:
        print("Usage: python telegram_trade_monitor.py <mint>")
        return

    mint = sys.argv[1]
    msg, buttons = await generate_monitor_card(mint)
    
    # Output for OpenClaw to consume
    output = {
        "message": msg,
        "buttons": buttons
    }
    print(json.dumps(output))

if __name__ == "__main__":
    asyncio.run(main())
