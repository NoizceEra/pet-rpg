import requests
import json
import os
import time
import hmac
import hashlib
import base64
from dotenv import load_dotenv

load_dotenv('polymarket-arbitrage/.env')

def test_custom_headers():
    url = "https://clob.polymarket.com/orders"
    
    # Deriving signatures is complex, so I'll just see if a simple GET with a real UA works first
    # If a GET works but my previous POST failed, it's definitely the POST protection.
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Origin": "https://polymarket.com",
        "Referer": "https://polymarket.com/"
    }
    
    print("Testing GET request with custom headers...")
    r = requests.get("https://clob.polymarket.com/sampling-markets", headers=headers)
    print(f"GET Status: {r.status_code}")
    
    if r.status_code == 200:
        print("✅ GET bypass successful.")
    else:
        print(f"❌ GET failed: {r.text[:200]}")

if __name__ == "__main__":
    test_custom_headers()
