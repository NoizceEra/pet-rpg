import json
from urllib.request import urlopen, Request
from datetime import datetime

def get_gamma():
    # Fetch a lot of markets to find today's
    url = "https://gamma-api.polymarket.com/markets?limit=500&closed=false"
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = Request(url, headers=headers)
    with urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

markets = get_gamma()
today = "February 17"
found = False
for m in markets:
    q = m.get("question", "")
    if today in q and "Up or Down" in q:
        print(f"FOUND TODAY: {q} (Slug: {m.get('slug')})")
        found = True

if not found:
    print("No 'Up or Down' markets found for February 17.")
    # Show some other February 17 markets
    for m in markets[:50]:
        q = m.get("question", "")
        if today in q:
            print(f"OTHER TODAY: {q}")
