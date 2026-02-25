import httpx
import asyncio
import socket

async def test():
    print(f"Resolving: {socket.gethostbyname('api.jup.ag')}")
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get("https://quote-api.jup.ag/v6/quote?inputMint=So11111111111111111111111111111111111111112&outputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&amount=100000000&slippageBps=50")
            print(f"Status: {resp.status_code}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
