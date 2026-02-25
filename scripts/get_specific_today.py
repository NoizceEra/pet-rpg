import json
from urllib.request import urlopen, Request

def get_market(slug):
    url = f"https://gamma-api.polymarket.com/markets?slug={slug}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = Request(url, headers=headers)
    with urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

# The browser showed this slug for the 3:30 PM ET (1:30 PM MST) market
slug = "btc-updown-15m-1771360200"
print(json.dumps(get_market(slug), indent=2))
