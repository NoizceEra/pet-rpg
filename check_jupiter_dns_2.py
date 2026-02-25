import httpx
import asyncio
import json

async def test():
    async with httpx.AsyncClient() as client:
        for name in ["quote-api.jup.ag", "api.jup.ag", "jup.ag"]:
            try:
                resp = await client.get(f"https://dns.google/resolve?name={name}")
                print(f"{name}: {resp.json().get('Answer', 'No Answer')}")
            except Exception as e:
                print(f"Error {name}: {e}")

if __name__ == "__main__":
    asyncio.run(test())
