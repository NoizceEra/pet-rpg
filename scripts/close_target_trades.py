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

# Specifically close the USDC positions identified as active and wrong-dated
# 1. 82cff1b9-bf17-44ce-95f7-4d0c33ca1c28 (Atalanta Win - Feb 17) -> User wants to keep today's sports
# 2. 830eb932-f302-4d3d-bf32-5bae4b105ac3 (BTC Up/Down - Feb 17) -> Today's
# 3. 2e809e3a-f0d9-4947-9a18-93501870548a (Dortmund Win - Feb 17) -> Today's
# 4. 9d20384e-b734-44db-b2f7-7e6a1bcf59a0 (BTC Up/Down - Feb 18) -> WRONG DATE

wrong_positions = [
    {"mid": "9d20384e-b734-44db-b2f7-7e6a1bcf59a0", "shares": 2.8017, "side": "yes", "venue": "polymarket"}
]

for p in wrong_positions:
    print(f"Closing wrong-dated position: {p['mid']}")
    res = simmer_request("/api/sdk/trade", "POST", {
        "market_id": p['mid'],
        "side": p['side'],
        "action": "sell",
        "shares": p['shares'],
        "venue": p['venue']
    })
    print(f"Sell result: {res}")
