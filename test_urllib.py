import urllib.request
import json
import ssl

def test():
    url = "https://api.jup.ag/swap/v1/quote?inputMint=So11111111111111111111111111111111111111112&outputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&amount=100000000&slippageBps=50"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    # Create unverified context
    context = ssl._create_unverified_context()
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=context) as response:
            print(f"Status: {response.getcode()}")
            print(f"Body: {response.read().decode()[:200]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
