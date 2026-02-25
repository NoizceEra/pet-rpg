import httpx
import asyncio
import socket

async def test():
    ip = "3.160.107.9"
    print(f"Using IP: {ip}")
    async with httpx.AsyncClient(timeout=10, verify=False) as client:
        try:
            # Try HTTP if HTTPS is failing on IP
            resp = await client.get(f"http://{ip}/v6/quote?inputMint=So11111111111111111111111111111111111111112&outputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&amount=100000000&slippageBps=50", headers={"Host": "quote-api.jup.ag"})
            print(f"Status: {resp.status_code}")
            print(f"Text: {resp.text[:100]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
