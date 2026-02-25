import os
import json
import asyncio
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# PATHS
WORKSPACE_ROOT = Path(r"C:\Users\vclin_jjufoql\.openclaw\workspace")
POSITIONS_FILE = WORKSPACE_ROOT / "active_positions.json"
RPC_URL = "https://api.mainnet-beta.solana.com"
WALLET_ADDRESS = "BKVU94WsjhfwPHMKLPXQFc4s9n9T3GbXtFUUxY9W6uMw"

async def get_token_accounts():
    async with httpx.AsyncClient(timeout=10) as client:
        # Standard Token Program
        payload_std = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                WALLET_ADDRESS,
                {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
                {"encoding": "jsonParsed"}
            ]
        }
        # Token-2022 Program
        payload_2022 = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                WALLET_ADDRESS,
                {"programId": "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"},
                {"encoding": "jsonParsed"}
            ]
        }
        
        results = []
        r_std = await client.post(RPC_URL, json=payload_std)
        if r_std.status_code == 200:
            results.extend(r_std.json().get("result", {}).get("value", []))
            
        r_2022 = await client.post(RPC_URL, json=payload_2022)
        if r_2022.status_code == 200:
            results.extend(r_2022.json().get("result", {}).get("value", []))
            
        return results

async def sync():
    print(f"Syncing holdings for {WALLET_ADDRESS}...")
    
    if not POSITIONS_FILE.exists():
        print("No positions file found.")
        # Create empty one if it doesn't exist
        with open(POSITIONS_FILE, "w") as f:
            json.dump({}, f)
        return

    with open(POSITIONS_FILE, "r") as f:
        positions = json.load(f)

    accounts = await get_token_accounts()
    
    # Map of mint -> uiAmount
    wallet_holdings = {}
    for acc in accounts:
        info = acc["account"]["data"]["parsed"]["info"]
        mint = info["mint"]
        amount = info["tokenAmount"]["uiAmount"]
        if amount > 0:
            wallet_holdings[mint] = amount

    updated = False
    new_positions = {}

    # 1. Check existing positions
    for mint, data in positions.items():
        if mint in wallet_holdings:
            # Token still exists, keep it
            new_positions[mint] = data
            # Update token count if it changed significantly (e.g. manual sell/buy)
            actual_amount = wallet_holdings[mint]
            # Convert UI amount to raw if possible or just store UI amount
            # The engine uses 'tokens_bought' which usually is raw.
            # For now, let's just keep it if it's there.
            print(f"Keeping {data.get('ticker', mint)}: {actual_amount}")
        else:
            print(f"Removing ghost position: {data.get('ticker', mint)}")
            updated = True

    # 2. Check for untracked tokens (excluding SOL/USDC)
    USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    for mint, amount in wallet_holdings.items():
        if mint not in new_positions and mint != USDC_MINT:
            print(f"ALERT: Untracked token found: {mint} (Amount: {amount})")
            # We don't auto-add yet as we lack metadata (ticker, entry_sol), 
            # but we could fetch it.
            # For now, just logging it.

    if updated or len(new_positions) != len(positions):
        with open(POSITIONS_FILE, "w") as f:
            json.dump(new_positions, f, indent=4)
        print("Positions file updated.")
    else:
        print("No changes needed.")

if __name__ == "__main__":
    asyncio.run(sync())
