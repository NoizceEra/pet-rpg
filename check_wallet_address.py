import json
from eth_account import Account

with open('moltwars-wallet.json', 'r') as f:
    key_bytes = json.load(f)

# The first 32 bytes of a Solana keypair are the private key
private_key_hex = bytes(key_bytes[:32]).hex()
print(f"Private Key Hex: 0x{private_key_hex}")

account = Account.from_key(private_key_hex)
print(f"EVM Address: {account.address}")
