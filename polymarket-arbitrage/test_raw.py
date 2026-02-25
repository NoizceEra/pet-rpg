import os
import json
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds

load_dotenv()

def test_raw():
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
    print("Fetching sampling markets...")
    try:
        resp = client.get_sampling_markets()
        print(f"Resp type: {type(resp)}")
        if isinstance(resp, dict):
            data = resp.get('data', [])
            print(f"Data count: {len(data)}")
            if data:
                print(f"Sample market: {data[0].get('question')}")
                print(f"Tags: {data[0].get('tags')}")
        else:
            print(f"Resp content: {str(resp)[:200]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_raw()
