import subprocess
import json
import os
from datetime import datetime
from pathlib import Path

# Paths
WORKSPACE_DIR = Path(r"C:\Users\vclin_jjufoql\.openclaw\workspace")
OUTPUT_FILE = WORKSPACE_DIR / "polymarket-arbitrage" / "market_intelligence.json"
MCP_CONFIG = WORKSPACE_DIR / "config" / "mcporter.json"

def get_market_news(query):
    try:
        cmd = [
            "npx", "mcporter", "--config", str(MCP_CONFIG),
            "call", "yahoo-finance.get_news", f"query={query}", "newsCount=3"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Error fetching news for {query}: {result.stderr}")
            return []
    except Exception as e:
        print(f"Exception fetching news for {query}: {e}")
        return []

def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting Market Intelligence Scan...")
    
    intel = {
        "timestamp": datetime.now().isoformat(),
        "assets": {}
    }
    
    for asset in ["BTC-USD", "ETH-USD", "SOL-USD"]:
        print(f"Scanning {asset}...")
        news = get_market_news(asset)
        intel["assets"][asset] = {
            "news": news
        }
    
    # Save to file
    with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
        json.dump(intel, f, indent=2)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Market Intelligence saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
