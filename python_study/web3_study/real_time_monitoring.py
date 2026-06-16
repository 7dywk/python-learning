from web3 import Web3
import time

w3 = Web3(Web3.HTTPProvider("https://rpc.ankr.com/eth/0b6736fcc614daa2d430206c00e47ba9f2541f0865d91d728f7b230abc03abba"))

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

contract = w3.eth.contract(address=address, abi=abi)
last_block = w3.eth.block_number

while True:
    current_block = w3.eth.block_number
    if current_block > last_block:
        logs = contract.events.Swap().get_logs(
            from_block=last_block,
            to_block=current_block,
        )
        for log in logs:
            args = log["args"]
            print(args)
        last_block = current_block
    time.sleep(12)