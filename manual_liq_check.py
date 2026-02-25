import httpx
import asyncio
import json

async def check():
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.raydium.io/v2/ammV3/ammPools")
        data = resp.json()
        pools = data.get('data', [])
        print(f"Total Pools: {len(pools)}")
        
        # Check high liquidity pools
        high_liq = [p for p in pools if float(p.get('tvl', 0)) > 8000]
        print(f"Pools > $8k: {len(high_liq)}")
        
        if high_liq:
            print(f"First 3 high liq: {high_liq[:3]}")

if __name__ == "__main__":
    asyncio.run(check())
