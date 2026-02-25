import httpx
import asyncio
import json

async def get_metadata(mint):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{mint}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        if resp.status_code == 200:
            return resp.json()
    return None

async def main():
    mints = [
        "DdfP2zL9ymJoZAFPnFDSHWL861wzrfgvU6bbMck2pump",
        "E7Xfasv5CRTNc6Xb16w36BZk3HRSogh8T4ZFimSnpump",
        "63p6ir6gGQ59ZCDN2iRGUkCrZyJvu2xaacRYBfKopump"
    ]
    results = {}
    for m in mints:
        results[m] = await get_metadata(m)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
