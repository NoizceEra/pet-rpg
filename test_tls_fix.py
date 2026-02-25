import requests
import ssl
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

class TlsAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=ssl.PROTOCOL_TLSv1_2 # Force TLS 1.2
        )

def test():
    url = "https://3.160.107.9/v6/quote"
    params = {
        "inputMint": "So11111111111111111111111111111111111111112",
        "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "amount": "100000000",
        "slippageBps": "50"
    }
    headers = {
        "Host": "quote-api.jup.ag",
        "User-Agent": "Mozilla/5.0"
    }
    
    session = requests.Session()
    session.mount("https://", TlsAdapter())
    
    try:
        resp = session.get(url, params=params, headers=headers, timeout=10, verify=False)
        print(f"Status: {resp.status_code}")
        print(f"Body: {resp.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
