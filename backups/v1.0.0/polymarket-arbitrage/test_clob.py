from py_clob_client.client import ClobClient, ApiCreds
import os
from dotenv import load_dotenv
import json

load_dotenv()

def test_clob():
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
        markets = resp if isinstance(resp, list) else resp.get('data', [])
        print(f"Found {len(markets)} markets.")
        
        arbs = []
        for m in markets:
            tokens = m.get('tokens', [])
            if len(tokens) >= 2:
                prices = [t.get('price') for t in tokens if t.get('price') is not None]
                if len(prices) == len(tokens):
                    psum = sum(prices)
                    if psum < 1.0:
                        arbs.append({
                            "question": m.get('question'),
                            "sum": psum,
                            "profit": (1.0 - psum) * 100
                        })
        
        if arbs:
            print(f"Found {len(arbs)} math arbs (gross):")
            for a in arbs:
                print(f" - {a['question']}: {a['profit']:.2f}%")
        else:
            print("No gross math arbs found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_clob()
