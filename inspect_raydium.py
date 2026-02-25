import httpx
import json

def inspect():
    try:
        resp = httpx.get("https://api.raydium.io/v2/ammV3/ammPools", timeout=15)
        print(f"Status: {resp.status_code}")
        data = resp.json()
        print(f"Type of data: {type(data)}")
        if isinstance(data, dict):
            print(f"Keys: {data.keys()}")
            if 'data' in data:
                print(f"Type of data['data']: {type(data['data'])}")
                if len(data['data']) > 0:
                    print(f"First item in data['data']: {type(data['data'][0])}")
                    print(data['data'][0])
        elif isinstance(data, list):
            print(f"First item in list: {type(data[0])}")
            print(data[0])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect()
