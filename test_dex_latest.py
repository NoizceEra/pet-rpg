import httpx
import asyncio
import json

async def test():
    async with httpx.AsyncClient() as client:
        # Check DexScreener Latest Pairs on Solana
        resp = await client.get("https://api.dexscreener.com/token-profiles/latest/v1")
        print(f"Status: {resp.status_code}")
        data = resp.json()
        print(f"Count: {len(data)}")
        # Filter for Solana
        sol_pairs = [p for p in data if p.get("chainId") == "solana"]
        print(f"Solana Count: {len(sol_pairs)}")
        if sol_pairs:
            print(f"Sample: {json.dumps(sol_pairs[0], indent=2)}")

if __name__ == "__main__":
    asyncio.run(test())
