import time
from web3 import Web3

alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/RXNzDG6oGSliYWM0F6HWs"
w3 = Web3(Web3.HTTPProvider(alchemy_url))
address = w3.to_checksum_address("0x28C6c06298d514Db089934071355E5743bf21d60")

previous_balance = w3.eth.get_balance(address)

while True:
    time.sleep(30)
    balance = w3.eth.get_balance(address)
    if balance != previous_balance:
        eth_old = w3.from_wei(previous_balance, "ether")
        eth_new = w3.from_wei(balance, "ether")
        previous_balance = balance
        print(f"Old: {eth_old} ETH")
        print(f"New: {eth_new} ETH")
