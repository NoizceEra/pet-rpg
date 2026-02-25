import httpx
import asyncio
import base58
import base64
import os
import json
import time
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

# CONFIG
PRIVATE_KEY = "3c1TQMUu24CvYpkFyrANnxAm6YzTN2Bc1aCTqhv9APpyHyXdZj19F6SLu9UYEmTcwVRVqQUAgnaNAQent37aCUxV"
RPC_URL = "https://api.mainnet-beta.solana.com"
# Public IPs for Jupiter to bypass DNS
JUPITER_IPS = ["18.238.136.73", "18.238.136.70", "18.238.136.43", "18.238.136.98"]
JUP_HOST = "api.jup.ag"
SOL_MINT = "So11111111111111111111111111111111111111112"

async def execute_trade(mint, amount_sol):
    print(f"Attempting buy for {mint}...")
    headers = {
        "Host": JUP_HOST,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    kp = Keypair.from_base58_string(PRIVATE_KEY)
    amount_lamports = int(amount_sol * 1e9)
    
    for ip in JUPITER_IPS:
        try:
            async with httpx.AsyncClient(verify=False, timeout=20) as client:
                # 1. QUOTE
                url_q = f"https://{ip}/swap/v1/quote?inputMint={SOL_MINT}&outputMint={mint}&amount={amount_lamports}&slippageBps=1500"
                resp_q = await client.get(url_q, headers=headers)
                if resp_q.status_code != 200: continue
                quote = resp_q.json()
                
                # 2. SWAP TX
                url_s = f"https://{ip}/swap/v1/swap"
                payload = {
                    "quoteResponse": quote,
                    "userPublicKey": str(kp.pubkey()),
                    "wrapAndUnwrapSol": True
                }
                resp_s = await client.post(url_s, json=payload, headers=headers)
                if resp_s.status_code != 200: continue
                
                tx_base64 = resp_s.json()["swapTransaction"]
                tx_bytes = base64.b64decode(tx_base64)
                unsigned_tx = VersionedTransaction.from_bytes(tx_bytes)
                
                # 3. SIGN
                signed_tx = VersionedTransaction(unsigned_tx.message, [kp.sign_message(unsigned_tx.message.serialize())])
                
                # 4. SEND
                async with httpx.AsyncClient() as rpc:
                    res = await rpc.post(RPC_URL, json={
                        "jsonrpc": "2.0", "id": 1, "method": "sendTransaction",
                        "params": [base64.b64encode(bytes(signed_tx)).decode(), {"skipPreflight": True}]
                    })
                    txid = res.json().get("result")
                    if txid:
                        print(f"SUCCESS! TX: {txid}")
                        return txid
        except Exception as e:
            print(f"IP {ip} failed: {e}")
            continue
    return None

if __name__ == "__main__":
    # Aggressive attempt on Joby Weeks Justice ($JOBY)
    mint = "2zSw9NDidsgotB2NDjZTYGQqQ7fsWtheZNJCfmL1pump"
    asyncio.run(execute_trade(mint, 0.04))
