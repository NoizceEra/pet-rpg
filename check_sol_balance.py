import httpx
import asyncio
import json

async def check_balance(address):
    rpc = "https://solana-mainnet.core.chainstack.com/bc71bed16350db49d622b7fa4d7c44d3"
    async with httpx.AsyncClient() as client:
        resp = await client.post(rpc, json={
            "jsonrpc": "2.0", "id": 1, "method": "getBalance",
            "params": [address]
        })
        data = resp.json()
        lamports = data.get("result", {}).get("value", 0)
        print(f"SOL: {lamports / 1e9}")

if __name__ == "__main__":
    asyncio.run(check_balance("BKVU94WsjhfwPHMKLPXQFc4s9n9T3GbXtFUUxY9W6uMw"))
