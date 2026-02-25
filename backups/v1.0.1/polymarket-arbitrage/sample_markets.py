from py_clob_client.client import ClobClient
import json

def sample():
    client = ClobClient(host="https://clob.polymarket.com")
    resp = client.get_sampling_markets()
    print(json.dumps(resp, indent=2))

if __name__ == "__main__":
    sample()
