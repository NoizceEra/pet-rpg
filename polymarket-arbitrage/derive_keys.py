import os
import asyncio
from py_clob_client.client import ClobClient
from dotenv import load_dotenv

async def main():
    load_dotenv()
    host = "https://clob.polymarket.com"
    chain_id = 137
    private_key = os.getenv("POLYMARKET_PRIVATE_KEY")
    
    if not private_key:
        print("POLYMARKET_PRIVATE_KEY not found in .env")
        return

    print("Attempting to derive API credentials...")
    client = ClobClient(
        host=host,
        chain_id=chain_id,
        key=private_key
    )
    
    try:
        api_creds = client.create_or_derive_api_creds()
        print("SUCCESS")
        print(f"API_KEY={api_creds.api_key}")
        print(f"API_SECRET={api_creds.api_secret}")
        print(f"API_PASSPHRASE={api_creds.api_passphrase}")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(main())
