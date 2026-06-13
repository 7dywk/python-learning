from web3 import Web3

alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/RXNzDG6oGSliYWM0F6HWs"
w3 = Web3(Web3.HTTPProvider(alchemy_url))

abi = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "sender", "type": "address"},
            {"indexed": False, "name": "amount0In", "type": "uint256"},
            {"indexed": False, "name": "amount1In", "type": "uint256"},
            {"indexed": False, "name": "amount0Out", "type": "uint256"},
            {"indexed": False, "name": "amount1Out", "type": "uint256"},
            {"indexed": True, "name": "to", "type": "address"},
        ],
        "name": "Swap",
        "type": "event",
    }
]

address = w3.to_checksum_address("0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc")

latest_block = w3.eth.block_number

contract = w3.eth.contract(address=address, abi=abi)

logs = contract.events.Swap().get_logs(
    from_block=latest_block - 8,
    to_block=latest_block
)

for log in logs:
    print(log)


