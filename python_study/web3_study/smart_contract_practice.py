from web3 import Web3

alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/RXNzDG6oGSliYWM0F6HWs"
w3 = Web3(Web3.HTTPProvider(alchemy_url))

address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
abi = [
    {
        "inputs": [],
        "name": "name",
        "outputs": [{"type": "string"}],
        "type": "function"
    },
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"type": "uint256"}],
        "type": "function"
    }
]

contract = w3.eth.contract(address=address, abi=abi)

result1 = contract.functions.name().call()
result2 = contract.functions.totalSupply().call()
clean_result = result2 / 10**6
print(f"{result1}\n{clean_result}")