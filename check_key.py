from eth_account import Account

key = "0x63d78fdcef72c7afe10aa7df9e1cf34ada39c4f152451ea2843dbf79bf0bc881"
account = Account.from_key(key)
print(f"Address: {account.address}")
