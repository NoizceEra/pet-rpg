import json
from urllib.request import urlopen, Request

def get_market(slug):
    url = f"https://gamma-api.polymarket.com/markets?slug={slug}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = Request(url, headers=headers)
    with urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

print(json.dumps(get_market("ucl-ben-rma-2026-02-17"), indent=2))
