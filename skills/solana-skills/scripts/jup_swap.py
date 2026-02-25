#!/usr/bin/env python3
"""
Jupiter Swap Operations (v2.1 - Overclocked)
Usage: python3 jup_swap.py <command> [args]

Commands:
  quote <input> <output> <amount>      Get swap quote (returns JSON)
  swap <input> <output> <amount>       Execute swap (returns JSON)
  sell <mint> <percent>                Sell % of token balance back to SOL (returns JSON)
"""

import os, sys, asyncio, argparse, base64, logging, json
from decimal import Decimal
from typing import Optional, Dict, Any

try:
    import aiohttp, base58
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    from solders.transaction import VersionedTransaction
except ImportError:
    sys.exit(1)

JUPITER_ULTRA_API_URL = os.environ.get("JUPITER_API_URL", "https://api.jup.ag/ultra/v1")
RPC_URL = os.environ.get("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
SOL_MINT = "So11111111111111111111111111111111111111112"

def get_keypair():
    return Keypair.from_base58_string(os.environ["SOLANA_PRIVATE_KEY"])

async def get_token_balance(mint: str, owner: str) -> int:
    async with aiohttp.ClientSession() as session:
        payload = {"jsonrpc":"2.0","id":1,"method":"getTokenAccountsByOwner","params":[owner,{"mint":mint},{"encoding":"jsonParsed"}]}
        async with session.post(RPC_URL, json=payload) as resp:
            data = await resp.json()
            try: return int(data['result']['value'][0]['account']['data']['parsed']['info']['tokenAmount']['amount'])
            except: return 0

async def get_order(input_mint, output_mint, amount, taker):
    api_key = os.environ["JUPITER_API_KEY"]
    params = {"inputMint": input_mint, "outputMint": output_mint, "amount": str(amount), "taker": taker}
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{JUPITER_ULTRA_API_URL}/order", params=params, headers={"x-api-key": api_key}) as resp:
            if resp.status != 200: return None
            return await resp.json()

async def execute_order(signed_tx, request_id):
    api_key = os.environ["JUPITER_API_KEY"]
    serialized_tx = base64.b64encode(bytes(signed_tx)).decode('utf-8')
    payload = {"signedTransaction": serialized_tx, "requestId": request_id}
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{JUPITER_ULTRA_API_URL}/execute", json=payload, headers={"x-api-key": api_key}) as resp:
            if resp.status != 200: return None
            return await resp.json()

def cmd_quote(args):
    kp = get_keypair()
    amount = int(float(args.amount) * 1e9) if args.input_mint == SOL_MINT else int(args.amount)
    res = asyncio.run(get_order(args.input_mint, args.output_mint, amount, str(kp.pubkey())))
    print(json.dumps(res))

def cmd_swap(args):
    kp = get_keypair()
    amount_lamports = int(float(args.amount) * 1e9)
    order = asyncio.run(get_order(SOL_MINT, args.output_mint, amount_lamports, str(kp.pubkey())))
    if not order or not order.get("transaction"):
        print(json.dumps({"error": "No order"})); return
    tx_bytes = base64.b64decode(order["transaction"])
    signed_tx = VersionedTransaction(VersionedTransaction.from_bytes(tx_bytes).message, [kp])
    res = asyncio.run(execute_order(signed_tx, order["requestId"]))
    res["inAmount"] = order.get("inAmount")
    res["outAmount"] = order.get("outAmount")
    print(json.dumps(res))

def cmd_sell(args):
    kp = get_keypair()
    raw_balance = asyncio.run(get_token_balance(args.mint, str(kp.pubkey())))
    if raw_balance == 0:
        print(json.dumps({"error": "No balance"})); return
    sell_amount = int(raw_balance * (float(args.percent) / 100.0))
    order = asyncio.run(get_order(args.mint, SOL_MINT, sell_amount, str(kp.pubkey())))
    if not order or not order.get("transaction"):
        print(json.dumps({"error": "No order"})); return
    tx_bytes = base64.b64decode(order["transaction"])
    signed_tx = VersionedTransaction(VersionedTransaction.from_bytes(tx_bytes).message, [kp])
    res = asyncio.run(execute_order(signed_tx, order["requestId"]))
    res["outAmountSOL"] = order.get("outAmount")
    print(json.dumps(res))

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    q_p = sub.add_parser("quote")
    q_p.add_argument("input_mint"); q_p.add_argument("output_mint"); q_p.add_argument("amount")
    s_p = sub.add_parser("swap")
    s_p.add_argument("input_mint"); s_p.add_argument("output_mint"); s_p.add_argument("amount")
    l_p = sub.add_parser("sell")
    l_p.add_argument("mint"); l_p.add_argument("percent")
    args = parser.parse_args()
    if args.command == "quote": cmd_quote(args)
    elif args.command == "swap": cmd_swap(args)
    elif args.command == "sell": cmd_sell(args)

if __name__ == "__main__":
    main()
