import os
import asyncio
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, BalanceAllowanceParams, AssetType

async def main():
    host = "https://clob.polymarket.com"
    chain_id = 137
    private_key = "0x63d78fdcef72c7afe10aa7df9e1cf34ada39c4f152451ea2843dbf79bf0bc881"
    proxy_wallet = "0x28acb894553e26d745990e1f22dcd3cdad641ebb"
    
    api_creds = ApiCreds(
        api_key="970f71b8-514d-d1d7-d0bc-4de6b047da29",
        api_secret="5ulf-4ylybvSywYUddMyOZlwE_f2B1QAjKP9ulh4434=",
        api_passphrase="d678e70d0ee2a3717c244f53f3f8c1f65052f7e8493c563e69a3942b42d66031"
    )
    
    client = ClobClient(
        host=host,
        chain_id=chain_id,
        key=private_key,
        creds=api_creds,
        signature_type=1,
        funder=proxy_wallet
    )
    
    try:
        print("Checking COLLATERAL balance...")
        params = BalanceAllowanceParams(asset_type=AssetType.COLLATERAL, signature_type=1)
        balance = client.get_balance_allowance(params)
        print(f"Result: {balance}")
        
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(main())
