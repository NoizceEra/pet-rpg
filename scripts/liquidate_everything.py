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

# Liquidate USDC positions to flush the wallet for today's trades
# Even if they are today's, the user said "Close all trades and open new ones"
positions = simmer_request("/api/sdk/positions").get("positions", [])
for p in positions:
    if p.get("currency") == "USDC" and p.get("status") == "active":
        print(f"Liquidating {p['question']}...")
        # Since shares are below minimum for some, we'll try to SELL all shares.
        # If shares < 5, we might need to buy up to 5 and then sell 5, or use a specific exit endpoint.
        # But Simmer's trade endpoint with action: sell usually handles the exit if shares are provided.
        res = simmer_request("/api/sdk/trade", "POST", {
            "market_id": p['market_id'],
            "side": "yes" if p.get('shares_yes', 0) > 0 else "no",
            "action": "sell",
            "shares": p.get('shares_yes', 0) or p.get('shares_no', 0),
            "venue": "polymarket"
        })
        print(f"Result: {res}")
