import httpx
import asyncio
import socket

# Force IPv4
def create_client():
    transport = httpx.AsyncHTTPTransport(local_address="0.0.0.0")
    return httpx.AsyncClient(transport=transport, verify=False)

async def test():
    ip = "3.160.107.9" # quote-api.jup.ag
    url = f"https://{ip}/v6/quote?inputMint=So11111111111111111111111111111111111111112&outputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&amount=100000000&slippageBps=50"
    headers = {"Host": "quote-api.jup.ag", "User-Agent": "Mozilla/5.0"}
    
    async with create_client() as client:
        try:
            resp = await client.get(url, headers=headers)
            print(f"Status: {resp.status_code}")
            print(f"Body: {resp.text[:200]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
