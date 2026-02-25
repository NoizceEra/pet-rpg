import requests
import json

def check_clob(token_id):
    url = "https://clob.polymarket.com/book"
    r = requests.get(url, params={"token_id": token_id})
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:500]}")

if __name__ == "__main__":
    check_clob("8761893133236939041067755978771380257562758508767581695604709041285942487710")
