import json
import os
from solcx import compile_standard, install_solc
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# Install Solidity compiler (only first time)
install_solc("0.8.0")

# Read contract source
with open("contracts/QuadraticVoting.sol", "r") as file:
    contract_source = file.read()

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"QuadraticVoting.sol": {"content": contract_source}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]}
            }
        },
    },
    solc_version="0.8.0",
)

# Extract ABI and bytecode
abi = compiled_sol["contracts"]["QuadraticVoting.sol"]["QuadraticVoting"]["abi"]
bytecode = compiled_sol["contracts"]["QuadraticVoting.sol"]["QuadraticVoting"]["evm"]["bytecode"]["object"]

# Connect to local Ganache (default: http://127.0.0.1:7545 or 8545 depending on version)
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
if not w3.is_connected():
    # Try port 8545 (ganache-cli default)
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

w3.eth.default_account = w3.eth.accounts[0]

# Deploy
Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
tx_hash = Contract.constructor().transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = tx_receipt.contractAddress

print(f"Contract deployed at: {contract_address}")

# Save ABI and address for Flask app
os.makedirs("build", exist_ok=True)
with open("build/QuadraticVoting.abi", "w") as f:
    json.dump(abi, f)
with open("build/contract_address.txt", "w") as f:
    f.write(contract_address)

print("ABI and address saved to build/")