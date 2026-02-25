import json
from urllib.request import urlopen, Request

def get_gamma():
    url = "https://gamma-api.polymarket.com/markets?limit=100&closed=true&order=createdAt&ascending=false"
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = Request(url, headers=headers)
    with urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

markets = get_gamma()
for m in markets:
    q = m.get("question", "")
    print(f"- {q}")
