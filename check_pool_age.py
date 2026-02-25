import httpx
import asyncio
import json
import time

async def check():
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get("https://api.raydium.io/v2/ammV3/ammPools")
        data = resp.json()
        pools = data.get('data', [])
        
        # Sort by openTime descending
        sorted_pools = sorted(pools, key=lambda x: x.get('openTime', 0), reverse=True)
        
        print(f"Total Pools: {len(pools)}")
        print(f"Current Time: {time.time()}")
        
        for i in range(10):
            p = sorted_pools[i]
            age = time.time() - p.get('openTime', 0)
            print(f"Pool {p['id']}: Age {age/60:.1f}m | Liq: ${p.get('tvl', 0):.0f}")

if __name__ == "__main__":
    asyncio.run(check())
