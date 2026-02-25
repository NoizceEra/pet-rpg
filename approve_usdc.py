from web3 import Web3
from eth_account import Account
import json

# Polygon RPC
RPC_URL = "https://polygon-rpc.com"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Wallet
PRIVATE_KEY = "0x63d78fdcef72c7afe10aa7df9e1cf34ada39c4f152451ea2843dbf79bf0bc881"
account = Account.from_key(PRIVATE_KEY)

# USDC and Bridge
USDC_ADDRESS = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
BRIDGE_ADDRESS = "0x1231DEB6f5749EF6cE6943a275A1D3E7486F4EaE"

# Minimal ERC20 ABI for approve
ABI = [{"constant":False,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"type":"function"}]

contract = w3.eth.contract(address=Web3.to_checksum_address(USDC_ADDRESS), abi=ABI)

# Build approve tx (1 USDC = 1,000,000 units)
nonce = w3.eth.get_transaction_count(account.address)
tx = contract.functions.approve(Web3.to_checksum_address(BRIDGE_ADDRESS), 1000000).build_transaction({
    'from': account.address,
    'nonce': nonce,
    'gas': 100000,
    'gasPrice': w3.eth.gas_price,
    'chainId': 137
})

# Sign and send
signed_tx = account.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

print(f"Approval TX Hash: {tx_hash.hex()}")
