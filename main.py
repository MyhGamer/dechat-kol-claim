from web3 import Web3
import time
import json
bsc_rpc_endpoint = 'https://rpc.ankr.com/bsc' # рпс
w3 = Web3(Web3.HTTPProvider(bsc_rpc_endpoint))
private_key = '' # приватный ключ кошелька с которого будете клеймить
account_address = ''#адрес кошелька с которого будете клеймить
contract_address = '0x1aF375456e5B0Ebf609a7429844832a1F251A7bE' # адрес контракта для клейма
with open("abi.json",'r') as abi_file:
    contract_abi = json.load(abi_file)
with open("token.json",'r') as abi2_file:
    token_abi = json.load(abi2_file)
token_address = '0xD69ee2e508363FEd57f89917D5ca03e715ee5519' # контракт токена дечат


# Wallet address to send tokens
destination_wallet = Web3.to_checksum_address('адрес куда депазитить будете')

# Gas price and gas limit
gas_price = w3.to_wei('5', 'gwei')
gas_limit = 200000

# Timestamp when the claim becomes available  ( время когда открывается клейм типо не трогаем)
claim_timestamp = 1708942500 

# Function to wait until the specified timestamp
def wait_until_timestamp(target_timestamp):
    current_timestamp = int(time.time())
    if current_timestamp < target_timestamp:
        time_to_wait = target_timestamp - current_timestamp
        print(f"Waiting for {time_to_wait} seconds until the claim becomes available...")
        time.sleep(time_to_wait)

# Function to claim and send tokens
def claim_and_send_tokens():
    # Wait until the specified timestamp
    wait_until_timestamp(claim_timestamp)

    # Load contract
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)

    # Build transaction for claim function
    claim_transaction = contract.functions.claim().build_transaction({
        'from': account_address,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'nonce': w3.eth.get_transaction_count(account_address),
    })

    # Sign and send claim transaction
    signed_claim_transaction = w3.eth.account.sign_transaction(claim_transaction, private_key)
    claim_tx_hash = w3.eth.send_raw_transaction(signed_claim_transaction.rawTransaction)
    print(f"Claim Transaction Hash: {claim_tx_hash.hex()}")

    # Wait for the claim transaction to be mined
    w3.eth.wait_for_transaction_receipt(claim_tx_hash)
    time.sleep(2)
    # Build transaction for sending tokens to destination_wallet
    token_contract = w3.eth.contract(address=token_address, abi=token_abi)
    send_tokens_transaction = token_contract.functions.transfer(destination_wallet, token_contract.functions.balanceOf(account_address).call()).build_transaction({
        'from': account_address,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'nonce': w3.eth.get_transaction_count(account_address),
    })

    # Sign and send send_tokens_transaction
    signed_send_tokens_transaction = w3.eth.account.sign_transaction(send_tokens_transaction, private_key)
    send_tokens_tx_hash = w3.eth.send_raw_transaction(signed_send_tokens_transaction.rawTransaction)
    print(f"Send Tokens Transaction Hash: {send_tokens_tx_hash.hex()}")

    # Wait for the send_tokens_transaction to be mined
    w3.eth.wait_for_transaction_receipt(send_tokens_tx_hash)

# Execute the claim_and_send_tokens function
claim_and_send_tokens()
