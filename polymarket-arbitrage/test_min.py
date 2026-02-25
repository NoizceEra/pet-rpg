from py_clob_client.client import ClobClient, ApiCreds
from py_clob_client.clob_types import OrderArgs
from py_clob_client.constants import BUY
import os
from dotenv import load_dotenv

load_dotenv()

def test_min_order():
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
    
    # Let's try to place a 0.10 USDC order on a common market
    # e.g. "Will Trump win..." or something
    # Token ID from sample_markets: "104071616575689490708756996503755160411785604144351427331378560378097635400347" (Russia x Ukraine ceasefire)
    
    token_id = "104071616575689490708756996503755160411785604144351427331378560378097635400347"
    price = 0.40
    size = 0.25 # shares -> 0.25 * 0.40 = 0.10 USDC
    
    order = OrderArgs(
        token_id=token_id,
        price=price,
        size=size,
        side="buy"
    )
    
    print(f"Trying to place order of size {size} shares at {price} (~0.10 USDC)...")
    try:
        resp = client.create_order(order)
        print(f"Response: {resp}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_min_order()
