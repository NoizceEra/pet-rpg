import httpx
import asyncio
import time

async def check():
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get("https://api.raydium.io/v2/main/pairs")
        pools = resp.json()
        print(f"Total Standard Pools: {len(pools)}")
        
        # Sort by age (Raydium v2 doesn't have openTime in this list usually, check first item)
        print(f"First item keys: {list(pools[0].keys())}")
        
        # Check if there's any liquidity > 8k
        high_liq = [p for p in pools if float(p.get('liquidity', 0)) > 8000]
        print(f"Standard Pools > $8k: {len(high_liq)}")

if __name__ == "__main__":
    asyncio.run(check())
