import subprocess
import base64
import json
import os
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
import httpx

# CONFIG
PRIVATE_KEY = "3c1TQMUu24CvYpkFyrANnxAm6YzTN2Bc1aCTqhv9APpyHyXdZj19F6SLu9UYEmTcwVRVqQUAgnaNAQent37aCUxV"
RPC_URL = "https://api.mainnet-beta.solana.com"
IP = "18.238.136.43"
HOST = "api.jup.ag"
SOL_MINT = "So11111111111111111111111111111111111111112"

def execute(mint, amount_sol):
    print(f"Bypassing SSL with curl proxy for {mint}...")
    
    # 1. GET QUOTE via curl (insecure)
    amount_lamports = int(amount_sol * 1e9)
    url_q = f"https://{IP}/swap/v1/quote?inputMint={SOL_MINT}&outputMint={mint}&amount={amount_lamports}&slippageBps=1500"
    
    cmd_q = ["curl", "-s", "-k", "-H", f"Host: {HOST}", url_q]
    result_q = subprocess.run(cmd_q, capture_output=True, text=True)
    if result_q.returncode != 0:
        print(f"Curl Quote Failed: {result_q.stderr}")
        return
    
    try:
        quote = json.loads(result_q.stdout)
    except:
        print(f"Failed to parse quote: {result_q.stdout}")
        return

    # 2. GET SWAP TX via curl
    url_s = f"https://{IP}/swap/v1/swap"
    kp = Keypair.from_base58_string(PRIVATE_KEY)
    payload = {
        "quoteResponse": quote,
        "userPublicKey": str(kp.pubkey()),
        "wrapAndUnwrapSol": True
    }
    
    # Write payload to file for curl
    with open("payload.json", "w") as f:
        json.dump(payload, f)
        
    cmd_s = ["curl", "-s", "-k", "-X", "POST", "-H", f"Host: {HOST}", "-H", "Content-Type: application/json", "--data", "@payload.json", url_s]
    result_s = subprocess.run(cmd_s, capture_output=True, text=True)
    if result_s.returncode != 0:
        print(f"Curl Swap Failed: {result_s.stderr}")
        return

    try:
        swap_data = json.loads(result_s.stdout)
        tx_base64 = swap_data["swapTransaction"]
    except:
        print(f"Failed to parse swap: {result_s.stdout}")
        return

    # 3. SIGN & SEND
    tx_bytes = base64.b64decode(tx_base64)
    unsigned_tx = VersionedTransaction.from_bytes(tx_bytes)
    signed_tx = VersionedTransaction(unsigned_tx.message, [kp.sign_message(unsigned_tx.message.serialize())])
    
    res = httpx.post(RPC_URL, json={
        "jsonrpc": "2.0", "id": 1, "method": "sendTransaction",
        "params": [base64.b64encode(bytes(signed_tx)).decode(), {"skipPreflight": True}]
    })
    print(f"RESULT: {res.json()}")

if __name__ == "__main__":
    execute("2zSw9NDidsgotB2NDjZTYGQqQ7fsWtheZNJCfmL1pump", 0.04)
