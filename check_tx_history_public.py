import httpx
import asyncio

async def check():
    address = "BKVU94WsjhfwPHMKLPXQFc4s9n9T3GbXtFUUxY9W6uMw"
    rpc = "https://api.mainnet-beta.solana.com"
    async with httpx.AsyncClient() as client:
        resp = await client.post(rpc, json={
            "jsonrpc": "2.0", "id": 1, "method": "getSignaturesForAddress",
            "params": [address, {"limit": 5}]
        })
        print(f"Transactions: {json.dumps(resp.json(), indent=2)}")

if __name__ == "__main__":
    import json
    asyncio.run(check())
