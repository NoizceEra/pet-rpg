import socket
import httpx
import asyncio

async def test():
    # Attempt to resolve via multiple public DNS over HTTP if possible? No.
    # Let's try to just hit it via a proxy?
    # Or just try to find the IP via a web request to a DNS checker.
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get("https://dns.google/resolve?name=quote-api.jup.ag")
            data = resp.json()
            print(f"DNS Google: {json.dumps(data, indent=2)}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    import json
    asyncio.run(test())
