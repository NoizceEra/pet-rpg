from py_clob_client.client import ClobClient
import os
from dotenv import load_dotenv

load_dotenv()

def check_methods():
    client = ClobClient(host="https://clob.polymarket.com")
    print("\n--- get_market ---")
    help(client.get_market)
    print("\n--- get_sampling_markets ---")
    help(client.get_sampling_markets)
    print("\n--- create_order ---")
    help(client.create_order)

if __name__ == "__main__":
    check_methods()
