import httpx
import asyncio
import ssl
import base64
import json
import os
import time
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

# CONFIG
PRIVATE_KEY = "3c1TQMUu24CvYpkFyrANnxAm6YzTN2Bc1aCTqhv9APpyHyXdZj19F6SLu9UYEmTcwVRVqQUAgnaNAQent37aCUxV"
RPC_URL = "https://api.mainnet-beta.solana.com"
JUP_IP = "108.162.192.59" # IP found for quote-api.jup.ag
JUP_HOST = "quote-api.jup.ag"
SOL_MINT = "So11111111111111111111111111111111111111112"

async def execute_autonomous_trade(mint, amount_sol):
    print(f"Attempting autonomous buy for {mint} with {amount_sol} SOL...")
    
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    headers = {
        "Host": JUP_HOST,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient(verify=context) as client:
        try:
            # 1. GET QUOTE
            amount_lamports = int(amount_sol * 1e9)
            url_q = f"https://{JUP_IP}/v6/quote?inputMint={SOL_MINT}&outputMint={mint}&amount={amount_lamports}&slippageBps=1500"
            resp_q = await client.get(url_q, headers=headers)
            if resp_q.status_code != 200:
                print(f"Quote failed: {resp_q.status_code}")
                return
            quote = resp_q.json()
            
            # 2. GET SWAP TX
            url_s = f"https://{JUP_IP}/v6/swap"
            kp = Keypair.from_base58_string(PRIVATE_KEY)
            payload = {
                "quoteResponse": quote,
                "userPublicKey": str(kp.pubkey()),
                "wrapAndUnwrapSol": True
            }
            resp_s = await client.post(url_s, json=payload, headers=headers)
            if resp_s.status_code != 200:
                print(f"Swap failed: {resp_s.status_code}")
                return
            swap_tx_base64 = resp_s.json()["swapTransaction"]
            
            # 3. SIGN
            tx_bytes = base64.b64decode(swap_tx_base64)
            unsigned_tx = VersionedTransaction.from_bytes(tx_bytes)
            signed_tx = VersionedTransaction(unsigned_tx.message, [kp.sign_message(unsigned_tx.message.serialize())])
            
            # 4. SEND
            async with httpx.AsyncClient() as rpc_client:
                res = await rpc_client.post(RPC_URL, json={
                    "jsonrpc": "2.0", "id": 1, "method": "sendTransaction",
                    "params": [base64.b64encode(bytes(signed_tx)).decode(), {"skipPreflight": True}]
                })
                print(f"Transaction sent: {res.json()}")
                
        except Exception as e:
            print(f"Execution error: {e}")

if __name__ == "__main__":
    # Test with 0.01 SOL on SOLSCAN
    asyncio.run(execute_autonomous_trade("5yaso9QHcqCmD7xegZvgRqa8J9RxjX2RtmK16frKpump", 0.01))
