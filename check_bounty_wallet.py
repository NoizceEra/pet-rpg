import time
import json
import subprocess
import sys

def get_balance(address, token, network):
    cmd = [
        "python", 
        r"C:\Users\vclin_jjufoql\.openclaw\workspace\skills\cryptowallet\scripts\balance_checker.py", 
        address, 
        "--network", network, 
        "--token", token
    ]
    for i in range(3):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                print(f"Attempt {i+1} failed: {result.stderr}")
                if "rate limit" in result.stderr.lower():
                    time.sleep(11)
                else:
                    break
        except Exception as e:
            print(f"Error: {e}")
            break
    return None

def main():
    wallet = "0xe5363DD6410E06ca5A2e2Ab46854FD044e16612f"
    native_usdc = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
    bridged_usdc = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
    
    print(f"Checking {wallet} for USDC on Polygon...")
    
    native_res = get_balance(wallet, native_usdc, "polygon")
    bridged_res = get_balance(wallet, bridged_usdc, "polygon")
    
    output = {
        "native": native_res,
        "bridged": bridged_res
    }
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
