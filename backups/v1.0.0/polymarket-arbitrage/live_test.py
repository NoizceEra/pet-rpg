import os
import json
import time
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs
import py_clob_client.http_helpers.helpers as helpers

load_dotenv('polymarket-arbitrage/.env')

# Monkey-patch User-Agent to bypass Cloudflare 403
original_overload = helpers.overloadHeaders
def patched_overload(method, headers):
    headers = original_overload(method, headers)
    headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    return headers
helpers.overloadHeaders = patched_overload

HOST = "https://clob.polymarket.com"
CHAIN_ID = 137

def get_client():
    creds = ApiCreds(
        api_key=os.getenv("POLYMARKET_API_KEY"),
        api_secret=os.getenv("POLYMARKET_API_SECRET"),
        api_passphrase=os.getenv("POLYMARKET_API_PASSPHRASE")
    )
    return ClobClient(host=HOST, key=os.getenv("POLYMARKET_PRIVATE_KEY"), chain_id=CHAIN_ID, creds=creds)

def live_smoke_test():
    client = get_client()
    print("--- Polymarket LIVE SMOKE TEST (Patched UA) ---")
    
    # 1. Fetch some markets to find a test target
    print("Fetching sample markets...")
    resp = client.get_sampling_markets()
    markets = resp.get('data', [])
    
    target_token = None
    target_price = 0.01
    target_question = ""
    
    for m in markets:
        tokens = m.get('tokens', [])
        for t in tokens:
            price = t.get('price')
            # Look for something very cheap
            if price and 0.005 <= price <= 0.02:
                target_token = t.get('token_id')
                target_price = price
                target_question = m.get('question')
                break
        if target_token: break
        
    if not target_token:
        print("Could not find a suitable $0.01 outcome for testing.")
        return

    print(f"Targeting: {target_question}")
    print(f"Token ID: {target_token} @ ${target_price}")
    
    # 2. Prepare the order
    # Size 10 shares @ $0.0185 = $0.185 total
    order_args = OrderArgs(
        price=target_price,
        size=10.0,
        side="BUY",
        token_id=target_token
    )
    
    print(f"Placing 10 share BUY limit order at ${target_price}...")
    
    try:
        # Create and post the order
        signed_order = client.create_order(order_args)
        resp = client.post_order(signed_order)
        
        print("--- API RESPONSE ---")
        print(json.dumps(resp, indent=2))
        
        if resp.get('success'):
            print("✅ SMOKE TEST SUCCESSFUL! Order placed.")
        else:
            print(f"❌ SMOKE TEST FAILED: {resp.get('error')}")
            
    except Exception as e:
        print(f"❌ EXECUTION EXCEPTION: {e}")

if __name__ == "__main__":
    live_smoke_test()
