import httpx
import asyncio

async def main():
    mints = [
        "7Uhq9sPuWRGVFHB4tQztEcqh6tbLJu2GqXaeQJS8pump",
        "F6Pak9EH2xrhcvzcvzW4Mz7s31HxccRTLzAZPLYkpump",
        "AjZ2pixdhvANRvPb68ouTGf4ZJJpsHbjQaXpoBPstnbw",
        "9eKqU5sQ1sN6fW3eF7s7s7s7s7s7s7s7s7s7s7s7s7s" # Dummy
    ]
    async with httpx.AsyncClient() as client:
        for mint in mints:
            try:
                r = await client.get(f"https://api.dexscreener.com/latest/dex/tokens/{mint}")
                data = r.json()
                pair = data.get("pairs", [{}])[0]
                name = pair.get("baseToken", {}).get("name", "???")
                symbol = pair.get("baseToken", {}).get("symbol", "???")
                print(f"{mint}: {name} ({symbol})")
            except:
                pass

if __name__ == "__main__":
    asyncio.run(main())
