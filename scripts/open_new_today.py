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

# Execute Today's BTC Sprint (Feb 17)
# 1:45 PM MST window (3:45 PM ET)
polymarket_url = "https://polymarket.com/event/btc-updown-15m-1771360200"

print(f"Opening position for today's market: {polymarket_url}")
trade_res = simmer_request("/api/sdk/trade", "POST", {
    "market_id": "830eb932-f302-4d3d-bf32-5bae4b105ac3", # Bitcoin Up or Down - Feb 17
    "side": "yes",
    "amount": 5.0,
    "venue": "polymarket",
    "reasoning": "Fresh entry for today's window (Feb 17) as requested. Momentum scalp."
})
print(f"Trade result: {trade_res}")
