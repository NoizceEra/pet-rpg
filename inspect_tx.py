import httpx
import json
import asyncio

async def main():
    rpc = 'https://api.mainnet-beta.solana.com'
    sig = '48c79P8aMkSoaRAwNUAGCoisGpDUvrasGH4sxALKoLx59LNJBMKtAu3MSVCWvnmGbUoxsjX12f23QMrCenVstMJ2'
    payload = {'jsonrpc': '2.0', 'id': 1, 'method': 'getTransaction', 'params': [sig, {'encoding': 'json', 'maxSupportedTransactionVersion': 0}]}
    async with httpx.AsyncClient() as client:
        r = await client.post(rpc, json=payload)
        tx = r.json().get('result')
        if tx:
            meta = tx.get('meta')
            post = meta.get('postTokenBalances', [])
            pre = meta.get('preTokenBalances', [])
            print("Pre:")
            for b in pre:
                print(f"  {b.get('mint')}: {b.get('uiTokenAmount', {}).get('uiAmount')}")
            print("Post:")
            for b in post:
                print(f"  {b.get('mint')}: {b.get('uiTokenAmount', {}).get('uiAmount')}")

if __name__ == "__main__":
    asyncio.run(main())
