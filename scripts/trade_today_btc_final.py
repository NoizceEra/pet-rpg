import json
from urllib.request import urlopen, Request

API_KEY = "sk_live_38fa4a2da03b639e0078b6e7f5329cc1e5e0040558197ecbf1643f3d63c099dd"

def simmer_request(path, method="GET", data=None):
    url = f"https://api.simmer.markets{path}"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data else None
    req = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}

# Execute Today's BTC 15m Sprint (Feb 17 3:30-3:45 PM ET)
polymarket_url = "https://polymarket.com/event/btc-updown-15m-1771360200"

# 1. Import
print("Importing today's market...")
import_res = simmer_request("/api/sdk/markets/import", "POST", {"polymarket_url": polymarket_url})
print(f"Import: {import_res}")

market_id = import_res.get("market_id")

if market_id:
    # 2. Trade
    print(f"Trading market: {market_id}")
    trade_res = simmer_request("/api/sdk/trade", "POST", {
        "market_id": market_id,
        "side": "yes",
        "amount": 5.0,
        "venue": "polymarket",
        "reasoning": "BTC showing strength in the 1:30 PM window, momentum scalp for real today (Feb 17)."
    })
    print(f"Trade result: {trade_res}")
else:
    print("Failed to get market ID.")
