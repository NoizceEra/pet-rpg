import httpx
import json
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        r = await client.get("https://api.dexscreener.com/latest/dex/search/?q=Hopecoin")
        pairs = r.json().get("pairs", [])
        for p in pairs[:5]:
            print(f"{p['baseToken']['symbol']}: {p['baseToken']['address']}")

if __name__ == "__main__":
    asyncio.run(main())
