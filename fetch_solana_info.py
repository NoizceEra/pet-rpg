import httpx
import asyncio
import json

async def get_info():
    address = "BKVU94WsjhfwPHMKLPXQFc4s9n9T3GbXtFUUxY9W6uMw"
    # Try a few RPCs
    rpcs = [
        "https://api.mainnet-beta.solana.com",
        "https://solana-api.projectserum.com",
        "https://rpc.ankr.com/solana"
    ]
    
    print(f"Checking wallet: {address}")
    
    for rpc in rpcs:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(rpc, json={
                    "jsonrpc": "2.0", "id": 1, "method": "getBalance",
                    "params": [address]
                })
                if resp.status_code == 200:
                    data = resp.json()
                    if "result" in data:
                        balance = data["result"]["value"] / 1e9
                        print(f"RPC {rpc} -> Balance: {balance} SOL")
                        break
                    else:
                        print(f"RPC {rpc} -> Error: {data.get('error')}")
                else:
                    print(f"RPC {rpc} -> Status: {resp.status_code}")
        except Exception as e:
            print(f"RPC {rpc} -> Exception: {e}")

if __name__ == "__main__":
    asyncio.run(get_info())
