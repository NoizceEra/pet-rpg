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

# Hard liquidation of active USDC positions to clear space
positions_to_close = [
    {"mid": "9d20384e-b734-44db-b2f7-7e6a1bcf59a0", "shares": 2.8017},
    {"mid": "2e809e3a-f0d9-4947-9a18-93501870548a", "shares": 7.0422},
    {"mid": "82cff1b9-bf17-44ce-95f7-4d0c33ca1c28", "shares": 59.0909},
    {"mid": "830eb932-f302-4d3d-bf32-5bae4b105ac3", "shares": 17.0586}
]

for p in positions_to_close:
    print(f"Liquidating {p['mid']}...")
    res = simmer_request("/api/sdk/trade", "POST", {
        "market_id": p['mid'],
        "side": "yes",
        "action": "sell",
        "shares": p['shares'],
        "venue": "polymarket"
    })
    print(f"Result: {res}")
