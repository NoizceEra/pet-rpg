import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        try:
            # Query Google DNS over HTTPS
            resp = await client.get("https://dns.google/resolve?name=quote-api.jup.ag")
            data = resp.json()
            if "Answer" in data:
                print(f"IP: {data['Answer'][0]['data']}")
            else:
                print("No answer from Google DNS")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
