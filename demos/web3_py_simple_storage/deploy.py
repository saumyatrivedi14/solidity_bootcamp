from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
    # print(simple_storage_file)

# Compile Solidity settings
install_solc("0.8.0")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.8.0",
)

# create a readable ABI JSON file
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# things needed to deploy our contract
# get bytecode from the JSON
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get ABI from the JSON
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

## setup blockchain env to run the contract on
## this can be done using Ganache, which can create local simulated blockchain
# RPC server network details
# Ganache Details
local_ganache_link = "http://0.0.0.0:8545"
local_ganache_chain_id = 1337
local_ganache_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
local_ganache_private_key = os.getenv("GANACHE_IDX0_PRIVATE_KEY")

# Rinkeby Testnet (using Infura.io)
rinkeby_link = "https://rinkeby.infura.io/v3/a407c1ffada842a79c1d89a23b51fdd3"
rinkeby_chain_id = 4
metamask_address = "0xfc4bab56F0D98924f13e438bc399B5D038B85A3F"
metamask_private_key = os.getenv("METAMASK_PRIVATE_KEY")

# Select network
w3 = Web3(Web3.HTTPProvider(rinkeby_link))
# Network ID / Chain ID (Blockchain ID)
chain_id = rinkeby_chain_id
# Address and Private Key to deploy from
my_address = metamask_address
private_key = metamask_private_key


## Steps to carry our a Transaction on the local chain
# create a contract object
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)

# 1. create the transaction (object)
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
        "gasPrice": w3.eth.gas_price,
    }
)

# 2. sign the transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

# 3. send the transaction
print("Deploying contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployment complete!")

## Interacting with the contract
# To interact with a contract we need two things:
# 1. Contract Address
# 2. Contract ABI
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

## There are two ways to interact with a contract:
# 1. Call (Blue button in Remix) -> Simulate maling the call and getting a return value
# 2. Transact (Orange button in Remix) -> Actually make a state change
print(simple_storage.functions.retrieve().call())
store_txn = simple_storage.functions.store(15).buildTransaction(
    {
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce + 1,
        "gasPrice": w3.eth.gas_price,
    }
)
signed_Store_txn = w3.eth.account.sign_transaction(store_txn, private_key=private_key)
tx_hash = w3.eth.send_raw_transaction(signed_Store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(simple_storage.functions.retrieve().call())
