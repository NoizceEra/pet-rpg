from web3 import Web3
import json

# Polygon USDC
USDC_ADDRESS = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
WALLET_ADDRESS = "0xe5363DD6410E06ca5A2e2Ab46854FD044e16612f"
BRIDGE_ADDRESS = "0x1231DEB6f5749EF6cE6943a275A1D3E7486F4EaE"

# Minimal ERC20 ABI for allowance
ABI = [{"constant":True,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"type":"function"}]

w3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
contract = w3.eth.contract(address=USDC_ADDRESS, abi=ABI)
allowance = contract.functions.allowance(WALLET_ADDRESS, BRIDGE_ADDRESS).call()

print(f"Allowance: {allowance}")
