import httpx
import asyncio
import json

async def test():
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get("https://api.raydium.io/v2/ammV3/ammPools")
        data = resp.json()
        pools = data.get('data', [])
        print(f"Total pools: {len(pools)}")
        print(f"First 3: {pools[:3]}")
        print(f"Last 3: {pools[-3:]}")

if __name__ == "__main__":
    asyncio.run(test())
