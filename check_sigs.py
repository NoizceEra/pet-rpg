import httpx
import json
import asyncio

async def main():
    owner = 'BKVU94WsjhfwPHMKLPXQFc4s9n9T3GbXtFUUxY9W6uMw'
    rpc = 'https://api.mainnet-beta.solana.com'
    payload = {'jsonrpc': '2.0', 'id': 1, 'method': 'getSignaturesForAddress', 'params': [owner, {'limit': 50}]}
    async with httpx.AsyncClient() as client:
        r = await client.post(rpc, json=payload)
        sigs = r.json().get('result', [])
        for s in sigs:
            print(f"Sig: {s['signature']} | Time: {s['blockTime']}")

if __name__ == "__main__":
    asyncio.run(main())
