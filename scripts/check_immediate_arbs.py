import os
import requests
import json
import time
from datetime import datetime

SIMMER_API_KEY = "sk_live_67cde9c17d16218b380e3452a7dbd4d5711b4a1a3c59a58e3d838aa93248a1b0"
BASE_URL = "https://api.simmer.markets/api/sdk"

headers = {
    "Authorization": f"Bearer {SIMMER_API_KEY}",
    "Content-Type": "application/json"
}

def get_ask(token_id):
    if not token_id: return 1.0
    url = f"https://clob.polymarket.com/price?token_id={token_id}&side=buy"
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        return float(data.get('price', 1.0))
    except:
        return 1.0

def scan():
    print(f"Scanning immediate today markets at {datetime.now()}...")
    
    # Target markets from the previous search
    targets = [
        {"id": "c8ec37cb-7f08-484d-889e-c4fafbbe58a6", "q": "Bitcoin 12:45PM-12:50PM"},
        {"id": "75fa3dd3-4663-499f-8def-5d1be16a010b", "q": "Bitcoin 12:50PM-12:55PM"},
        {"id": "5948ccf7-9c1a-4f77-b7f5-6b3fda20e885", "q": "Ethereum 1:45PM-2:00PM"}
    ]
    
    for t in targets:
        # Get market details to get token IDs
        m_url = f"{BASE_URL}/markets?ids={t['id']}"
        m_resp = requests.get(m_url, headers=headers)
        m_data = m_resp.json().get('markets', [{}])[0]
        
        token_yes = m_data.get('polymarket_token_id')
        token_no = m_data.get('polymarket_no_token_id')
        
        if not token_yes or not token_no:
            print(f"Market {t['q']} missing tokens.")
            continue
            
        ask_yes = get_ask(token_yes)
        ask_no = get_ask(token_no)
        combined = ask_yes + ask_no
        
        print(f"Market: {t['q']}")
        print(f"  YES Ask: {ask_yes:.4f} | NO Ask: {ask_no:.4f} | Sum: {combined:.4f}")
        
        if combined < 1.0:
            print(f"  !!! ARB FOUND !!! Edge: {1.0-combined:.4f}")

if __name__ == "__main__":
    scan()
