import json
from urllib.request import urlopen, Request
from datetime import datetime, timezone, timedelta

def get_gamma():
    url = "https://gamma-api.polymarket.com/markets?limit=100&closed=false&order=createdAt&ascending=false"
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = Request(url, headers=headers)
    with urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def find_today_markets():
    markets = get_gamma()
    today_str = "February 17" # Today's date
    today_markets = []
    for m in markets:
        q = m.get("question", "")
        if today_str in q:
            today_markets.append(m)
    return today_markets

today_markets = find_today_markets()
print(f"Found {len(today_markets)} markets for today.")
for m in today_markets:
    print(f"- {m.get('question')} (Slug: {m.get('slug')})")
