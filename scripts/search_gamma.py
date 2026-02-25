import json
from urllib.request import urlopen, Request

def get_gamma(q):
    url = f"https://gamma-api.polymarket.com/markets?limit=5&closed=false&q={q}"
    req = Request(url)
    with urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

print(json.dumps(get_gamma("Benfica"), indent=2))
print(json.dumps(get_gamma("Dortmund"), indent=2))
