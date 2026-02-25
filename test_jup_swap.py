import subprocess
import os

env = os.environ.copy()
env["SOLANA_PRIVATE_KEY"] = "3c1TQMUu24CvYpkFyrANnxAm6YzTN2Bc1aCTqhv9APpyHyXdZj19F6SLu9UYEmTcwVRVqQUAgnaNAQent37aCUxV"

# Using the SOL symbol directly as supported by the script
command = ["python", r"skills\solana-skills\scripts\jup_swap.py", "quote", "SOL", "USDC", "0.01"]

result = subprocess.run(command, capture_output=True, text=True, env=env)
print(f"Stdout: {result.stdout}")
print(f"Stderr: {result.stderr}")
