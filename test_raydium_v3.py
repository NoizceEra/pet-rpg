import httpx
import asyncio
import json

async def test():
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.raydium.io/v2/ammV3/ammPools")
        data = resp.json()
        print(f"Type: {type(data)}")
        if isinstance(data, dict):
            print(f"Keys: {list(data.keys())}")
            if 'data' in data:
                print(f"Data count: {len(data['data'])}")
                print(f"Sample: {json.dumps(data['data'][0], indent=2)}")
        else:
            print(f"List count: {len(data)}")
            print(f"Sample: {json.dumps(data[0], indent=2)}")

if __name__ == "__main__":
    asyncio.run(test())
