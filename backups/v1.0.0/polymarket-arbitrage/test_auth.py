from py_clob_client.client import ClobClient
import os
from dotenv import load_dotenv

load_dotenv()

def test_auth():
    print("Checking ClobClient initialization...")
    # This is just to see the signature/help
    help(ClobClient.__init__)

if __name__ == "__main__":
    test_auth()
