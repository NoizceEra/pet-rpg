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

# Close Feb 18 positions
positions = simmer_request("/api/sdk/positions").get("positions", [])
for p in positions:
    if p.get("status") == "active" and "February 18" in p.get("question", ""):
        print(f"Closing position: {p['question']}")
        # Sell YES shares
        if p['shares_yes'] > 0:
            res = simmer_request("/api/sdk/trade", "POST", {
                "market_id": p['market_id'],
                "side": "yes",
                "action": "sell",
                "shares": p['shares_yes']
            })
            # Actually, standard Simmer SDK uses 'side' and 'amount'. 
            # If I want to close YES, I should sell YES.
            # I'll try 'action': 'sell' and 'side': 'yes'.
            print(f"Sell result: {res}")
