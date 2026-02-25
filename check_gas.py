from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
gas_price = w3.eth.gas_price
print(f"Gas Price (Wei): {gas_price}")
print(f"Gas Price (Gwei): {gas_price / 1e9}")
