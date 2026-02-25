#!/usr/bin/env python3
import json
import httpx
import asyncio
from pathlib import Path

WORKSPACE_ROOT = Path(r"C:\Users\vclin_jjufoql\.openclaw\workspace")
POSITIONS_FILE = WORKSPACE_ROOT / "active_positions.json"

async def get_token_prices(mints):
    if not mints:
        return {}
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{','.join(mints)}"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                prices = {}
                for pair in data.get("pairs", []):
                    mint = pair.get("baseToken", {}).get("address")
                    if mint and mint not in prices:
                        prices[mint] = float(pair.get("priceNative", 0))
                return prices
    except Exception:
        pass
    return {}

async def main():
    if not POSITIONS_FILE.exists():
        print(json.dumps({"text": "No active positions found.", "buttons": []}))
        return

    with open(POSITIONS_FILE, "r") as f:
        positions = json.load(f)

    if not positions:
        print(json.dumps({"text": "No active positions found.", "buttons": []}))
        return

    mints = list(positions.keys())
    prices = await get_token_prices(mints)

    total_entry = 0
    total_value = 0
    pos_lines = []
    
    # We'll create buttons for the top 5 positions to keep it clean
    buttons = []
    row = []

    for mint, pos in positions.items():
        price = prices.get(mint, 0)
        entry = pos.get("entry_sol", 0)
        holdings = pos.get("tokens_bought", 0) / 1e6 # assuming 6 decimals for pump
        
        current_value = holdings * price
        roi = (current_value / entry) if entry > 0 else 0
        
        total_entry += entry
        total_value += current_value
        
        status_emoji = "📈" if roi >= 1 else "📉"
        pos_lines.append(f"{status_emoji} *{pos.get('ticker', '???')}*: {roi:.2f}x ({current_value:.3f} SOL)")
        
        btn = {"text": pos.get("ticker", "???"), "callback_data": f"/vulture_monitor_{mint}"}
        row.append(btn)
        if len(row) == 3:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    total_profit = total_value - total_entry
    profit_pct = (total_profit / total_entry * 100) if total_entry > 0 else 0
    profit_emoji = "💰" if total_profit >= 0 else "🛑"

    summary = (
        f"💼 *ACTIVE POSITIONS*\n\n"
        + "\n".join(pos_lines) + "\n\n"
        + f"{profit_emoji} *Total Profit/Loss: {total_profit:+.4f} SOL ({profit_pct:+.1f}%)*\n"
        + f"Total Invested: {total_entry:.3f} SOL\n"
        + f"Total Value: {total_value:.3f} SOL"
    )

    # Add bottom controls
    buttons.append([
        {"text": "🔄 Refresh", "callback_data": "/vulture_positions"},
        {"text": "🔙 Back to Menu", "callback_data": "/vulture"}
    ])

    print(json.dumps({"text": summary, "buttons": buttons}))

if __name__ == "__main__":
    asyncio.run(main())
