import base58
from eth_account import Account

key_b58 = "3c1TQMUu24CvYpkFyrANnxAm6YzTN2Bc1aCTqhv9APpyHyXdZj19F6SLu9UYEmTcwVRVqQUAgnaNAQent37aCUxV"
key_bytes = base58.b58decode(key_b58)
print(f"Key bytes length: {len(key_bytes)}")

# If it's a 64-byte Solana keypair, the first 32 are the private key
if len(key_bytes) == 64:
    priv_bytes = key_bytes[:32]
elif len(key_bytes) == 32:
    priv_bytes = key_bytes
else:
    priv_bytes = key_bytes

print(f"Private key hex: 0x{priv_bytes.hex()}")

try:
    account = Account.from_key(priv_bytes.hex())
    print(f"EVM Address: {account.address}")
except Exception as e:
    print(f"Error: {e}")
