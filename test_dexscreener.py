import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.dexscreener.com/token-profiles/latest/v1")
        print(f"Status: {resp.status_code}")
        print(f"Data: {resp.text[:500]}")

if __name__ == "__main__":
    asyncio.run(test())
