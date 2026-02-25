import httpx
import asyncio
import ssl

async def test():
    # Force IPv4 and specific TLS version
    # This addresses the SSLV3_ALERT_HANDSHAKE_FAILURE
    
    url = "https://18.238.136.73/v6/quote?inputMint=So11111111111111111111111111111111111111112&outputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&amount=100000000&slippageBps=50"
    
    headers = {
        "Host": "api.jup.ag",
        "User-Agent": "Mozilla/5.0"
    }
    
    # Use a custom SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    # Disable SNI by not passing server_hostname? No, httpx needs it.
    # But we can use the transport directly.
    transport = httpx.AsyncHTTPTransport(local_address="0.0.0.0")
    
    async with httpx.AsyncClient(verify=context, transport=transport) as client:
        try:
            resp = await client.get(url, headers=headers)
            print(f"Status: {resp.status_code}")
            print(f"Body: {resp.text[:200]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
