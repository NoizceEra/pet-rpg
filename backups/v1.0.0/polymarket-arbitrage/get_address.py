from eth_account import Account
import os
from dotenv import load_dotenv

load_dotenv()

def get_addr():
    key = os.getenv("POLYMARKET_PRIVATE_KEY")
    if key:
        acc = Account.from_key(key)
        print(acc.address)

if __name__ == "__main__":
    get_addr()
