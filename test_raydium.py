import httpx
import asyncio
import json

async def test():
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get("https://api.raydium.io/v2/ammV3/ammPools")
        print(f"Status: {resp.status_code}")
        data = resp.json()
        if isinstance(data, dict):
            print(f"Keys: {list(data.keys())}")
            if 'data' in data:
                print(f"Data length: {len(data['data'])}")
                if len(data['data']) > 0:
                    print(f"First item: {data['data'][0]}")
        else:
            print(f"Length: {len(data)}")
            if len(data) > 0:
                print(f"First item: {data[0]}")

if __name__ == "__main__":
    asyncio.run(test())
