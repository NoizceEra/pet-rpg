import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        for name in ["quote.jup.ag", "v6.quote-api.jup.ag", "station.jup.ag"]:
            try:
                resp = await client.get(f"https://dns.google/resolve?name={name}")
                print(f"{name}: {resp.json().get('Answer', 'No Answer')}")
            except Exception as e:
                print(f"Error {name}: {e}")

if __name__ == "__main__":
    asyncio.run(test())
