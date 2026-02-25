import os
from dotenv import load_dotenv

load_dotenv()

print("Testing env variables...")
print(f"API_KEY exists: {bool(os.getenv('POLYMARKET_API_KEY'))}")
print(f"API_SECRET exists: {bool(os.getenv('POLYMARKET_API_SECRET'))}")
print(f"PRIVATE_KEY exists: {bool(os.getenv('POLYMARKET_PRIVATE_KEY'))}")
print("Done!")
