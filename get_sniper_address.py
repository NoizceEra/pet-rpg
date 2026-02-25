from solders.keypair import Keypair
import base58
import os

with open(r'C:\Users\vclin_jjufoql\.openclaw\workspace\skills\solana-sniper-bot\scripts\.env', 'r') as f:
    for line in f:
        if line.startswith('SOLANA_PRIVATE_KEY'):
            pk = line.split('=')[1].strip().strip('"').strip("'")
            keypair = Keypair.from_base58_string(pk)
            print(f"Address: {keypair.pubkey()}")
