from web3 import Web3
from eth_account import Account
import json

PRIVATE_KEY = "0x760e9aa6e73acd68d13f1ee36ea5d2db4fafd526bcec262097cfad1beab15c92"
CONTRACT_ADDRESS = "0x85ac2e065d4526FBeE6a2253389669a12318A412"
# Avalanche Fuji Testnet RPC URL
RPC_URL = "https://api.avax-test.network/ext/bc/C/rpc"

def load_abi():
    try:
        with open('NFT.abi', 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"cannot load NFT.abi: {e}")
        return None

def main():
    abi = load_abi()
    if not abi:
        print("load abi failed.")
        return
    
    # connect to Avalanche Fuji Testnet
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("connect to Avalanche Fuji Testnet failed.")
        return
    print("connect to Avalanche Fuji Testnet succeed.")
    
    # create account from private key
    account = Account.from_key(PRIVATE_KEY)
    address = account.address
    print(f"address: {address}")
    
    # check account balance
    balance = w3.eth.get_balance(address)
    print(f"account balance: {w3.from_wei(balance, 'ether')} AVAX")
    
    if balance == 0:
        print("warning: account balance = 0")
        return
    
    # create contract
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
    
    # get maxId
    try:
        max_id = contract.functions.maxId().call()
        print(f"maxId: {max_id}")
    except Exception as e:
        print(f"cannot access maxId: {e}")
        max_id = 2**64 
    
    best_nonce = 4 
    print(f"using nonce: {best_nonce}")
    # convert nonce to bytes32 form
    nonce_hex = hex(best_nonce)[2:].zfill(64)
    nonce_bytes32 = "0x" + nonce_hex
    
    # use claim method
    try:
        function_signature = contract.functions.claim(address, nonce_bytes32).build_transaction({
            'gas': 0,  
            'gasPrice': 0,
            'nonce': 0,
            'value': 0,
        })['data']
        
        # create transaction
        transaction = {
            'to': CONTRACT_ADDRESS,
            'gas': 3000000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(address),
            'data': function_signature,
            'chainId': 43113  # Avalanche Fuji testnet
        }
        
        print("create transaction succeed, next signature...")
        
        signed = w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)
        
        print("signature succeed，get rawTransaction...")
        
        # get raw_transaction
        raw_transaction = signed.raw_transaction
        print("get raw_transaction succeed.")
        
        print("send transaction...")
        
        # send transaction
        tx_hash = w3.eth.send_raw_transaction(raw_transaction)
        tx_hash_hex = tx_hash.hex()
        print(f"transaction sent: {tx_hash_hex}")
        
        # transaction confirmation process
        print("wait for transaction confirmation...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if tx_receipt['status'] == 1:
            print("NFT successful!")
            
            # check NFT account owns
            try:
                balance = contract.functions.balanceOf(address).call()
                print(f"account owns NFT amount: {balance}")
                
                if balance > 0:
                    token_id = contract.functions.tokenOfOwnerByIndex(address, 0).call()
                    print(f"NFT Token ID: {token_id}")
            except Exception as e:
                print(f"cannot access NFT details: {e}")
        else:
            print(f"transaction failed，status: {tx_receipt['status']}")
            
    except Exception as e:
        print(f"send transaction failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()