from py_clob_client.client import ClobClient, ApiCreds
import os
from dotenv import load_dotenv

load_dotenv()

def check_conn():
    creds = ApiCreds(
        api_key=os.getenv("POLYMARKET_API_KEY"),
        api_secret=os.getenv("POLYMARKET_API_SECRET"),
        api_passphrase=os.getenv("POLYMARKET_API_PASSPHRASE")
    )
    client = ClobClient(
        host="https://clob.polymarket.com",
        key=os.getenv("POLYMARKET_PRIVATE_KEY"),
        chain_id=137,
        creds=creds
    )
    print("Connecting to Polymarket...")
    try:
        # Check if we can get sampling markets (doesn't need L2 but checks connection)
        resp = client.get_sampling_markets()
        print(f"Connection Successful! Markets found: {len(resp) if isinstance(resp, list) else 'Many'}")
    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    check_conn()
