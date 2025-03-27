from web3 import Web3
from web3.middleware import geth_poa_middleware
import json

# connetct to Avalanche Fuji
w3 = Web3(Web3.HTTPProvider('https://api.avax-test.network/ext/bc/C/rpc'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

private_key = "0x760e9aa6e73acd68d13f1ee36ea5d2db4fafd526bcec262097cfad1beab15c92"  # 替换成你的私钥
account = w3.eth.account.from_key(private_key)

with open('NFT.abi', 'r') as f:
    contract_abi = json.load(f)

contract_address = "0x85ac2e065d4526FBeE8a2253389669a12318A412"

nft_contract = w3.eth.contract(address=contract_address, abi=contract_abi)

def claim_nft(nonce):
    try:
        tx = nft_contract.functions.claim(
            account.address,  
            nonce            
        ).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 200000,
            'gasPrice': w3.eth.gas_price
        })
        
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"NFT Claimed! Transaction Hash: {tx_hash.hex()}")
        return True
        
    except Exception as e:
        print(f"Failed to claim NFT (nonce={nonce}): {str(e)}")
        return False

if __name__ == "__main__":
    print(f"account: {account.address}")
    
    # try to claim NFT
    for nonce in range(0, 100): 
        print(f"尝试nonce={nonce}...")
        if claim_nft(nonce):
            break