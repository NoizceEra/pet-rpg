import httpx
import asyncio
import socket

async def test():
    ip = "3.160.107.9"
    print(f"Using IP: {ip}")
    # Force the hostname in the connection
    transport = httpx.AsyncHTTPTransport(local_address="0.0.0.0", retries=3)
    async with httpx.AsyncClient(timeout=10, base_url="https://quote-api.jup.ag") as client:
        try:
            # We can't easily override DNS in httpx without a custom resolver or complex transport
            # But let's try one more native hit to see if it was a fluke
            resp = await client.get("/v6/quote?inputMint=So11111111111111111111111111111111111111112&outputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&amount=100000000&slippageBps=50")
            print(f"Status: {resp.status_code}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
