from py_clob_client.client import ClobClient, ApiCreds
import os
from dotenv import load_dotenv
import json

load_dotenv()

HOST = "https://clob.polymarket.com"
CHAIN_ID = 137

def test_market():
    creds = ApiCreds(
        api_key=os.getenv("POLYMARKET_API_KEY"),
        api_secret=os.getenv("POLYMARKET_API_SECRET"),
        api_passphrase=os.getenv("POLYMARKET_API_PASSPHRASE")
    )
    client = ClobClient(
        host=HOST,
        key=os.getenv("POLYMARKET_PRIVATE_KEY"),
        chain_id=CHAIN_ID,
        creds=creds
    )
    
    # Let's try to get a market that we know exists from a recent scan
    # Or just get a list of sampling markets
    print("Fetching market data...")
    try:
        # We need a condition, but let's just try to list some
        # resp = client.get_markets()
        # help(client.get_market)
        pass
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_market()
