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

# Dortmund vs Atalanta multi-market arb
markets = [
    "2e809e3a-f0d9-4947-9a18-93501870548a", # Dortmund Win
    "629104e8-ac2f-472d-9c5e-efce7ffe7c9f", # Draw
    "82cff1b9-bf17-44ce-95f7-4d0c33ca1c28"  # Atalanta Win
]

for mid in markets:
    print(f"Buying Yes on {mid}...")
    res = simmer_request("/api/sdk/trade", "POST", {
        "market_id": mid,
        "side": "yes",
        "amount": 5.0,
        "venue": "polymarket",
        "reasoning": "Guaranteed outcome hedge across 3-way markets (Dortmund/Atalanta)."
    })
    print(f"Result: {res}")
