import httpx
import asyncio
import socket

# Hardcoded IP for quote-api.jup.ag found via public DNS check earlier
JUP_IP = "3.160.107.9" 

async def test():
    # Attempting to use the IP directly with the Host header
    headers = {
        "Host": "quote-api.jup.ag",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }
    async with httpx.AsyncClient(verify=False) as client:
        try:
            url = f"https://{JUP_IP}/v6/quote?inputMint=So11111111111111111111111111111111111111112&outputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&amount=100000000&slippageBps=50"
            resp = await client.get(url, headers=headers)
            print(f"Status: {resp.status_code}")
            print(f"Body: {resp.text[:200]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
