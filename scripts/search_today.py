import json
from urllib.request import urlopen, Request

def get_gamma():
    url = "https://gamma-api.polymarket.com/markets?limit=100&closed=false&q=February%2017"
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = Request(url, headers=headers)
    with urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

markets = get_gamma()
for m in markets:
    # Safe print for Windows consoles
    try:
        print(f"- {m.get('question')} (Slug: {m.get('slug')})")
    except UnicodeEncodeError:
        safe_q = m.get('question').encode('ascii', 'ignore').decode('ascii')
        print(f"- {safe_q} (Slug: {m.get('slug')})")
