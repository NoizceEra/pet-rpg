import httpx
import asyncio

async def test():
    # IP for quote-api.jup.ag
    ip = "3.160.107.9" 
    url = f"https://{ip}/v6/quote?inputMint=So11111111111111111111111111111111111111112&outputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&amount=100000000&slippageBps=50"
    headers = {
        "Host": "quote-api.jup.ag",
        "User-Agent": "Mozilla/5.0"
    }
    async with httpx.AsyncClient(verify=False) as client:
        try:
            resp = await client.get(url, headers=headers)
            print(f"Status: {resp.status_code}")
            print(f"Body: {resp.text[:200]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
