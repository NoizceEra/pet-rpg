import os
import requests
import json

API_KEY = "sk_live_67cde9c17d16218b380e3452a7dbd4d5711b4a1a3c59a58e3d838aa93248a1b0"
CLOB_URL = "https://clob.polymarket.com/book"

def get_best_ask(token_id):
    try:
        res = requests.get(CLOB_URL, params={"token_id": token_id}).json()
        asks = res.get("asks", [])
        if asks:
            return min(float(ask["price"]) for ask in asks)
    except:
        pass
    return None

markets = [
    {"id": "a87c2d2f-3f66-44f5-b114-6ee3a7400fc4", "name": "BTC 10:30-10:45", "y": "26735628836693886170081766989252411458536554220273345936838561356596360602057", "n": "86253518281340622266137057186763201355229833654053135150268813043769946173978"},
    {"id": "fff9d778-36c1-42fd-bea7-7ce48d76ae50", "name": "ETH 10:30-10:45", "y": "32241771014637353536547904822922162496354194265611424079291444676201471101793", "n": "24920932724054933317995313551466255266624415557867155711117210430838301231257"}
]

for m in markets:
    ay = get_best_ask(m["y"])
    an = get_best_ask(m["n"])
    if ay and an:
        total = ay + an
        print(f"{m['name']}: YES {ay:.4f} + NO {an:.4f} = {total:.4f}")
    else:
        print(f"{m['name']}: Could not fetch prices.")
