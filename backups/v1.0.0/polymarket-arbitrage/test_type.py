from py_clob_client.client import ClobClient
import os
from dotenv import load_dotenv

load_dotenv()

def test():
    client = ClobClient(host="https://clob.polymarket.com")
    resp = client.get_sampling_markets()
    print(f"Type: {type(resp)}")
    if isinstance(resp, dict):
        print(f"Keys: {resp.keys()}")
    elif isinstance(resp, list):
        print(f"Length: {len(resp)}")

if __name__ == "__main__":
    test()
