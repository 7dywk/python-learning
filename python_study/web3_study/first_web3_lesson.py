import time
from web3 import Web3
from datetime import datetime

alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/RXNzDG6oGSliYWM0F6HWs"
w3 = Web3(Web3.HTTPProvider(alchemy_url))
print(w3.is_connected())

print("-"*50)


address = w3.to_checksum_address("0x28C6c06298d514Db089934071355E5743bf21d60")
balance = w3.eth.get_balance(address)
result = w3.from_wei(balance, "ether")
print(result)

print("-"*50)

latest_block = w3.eth.get_block("latest")
print(latest_block["number"])
print(datetime.fromtimestamp(latest_block["timestamp"]))
print(len(latest_block["transactions"]))

print("-"*50)

tx_hash = w3.eth.get_transaction("0x240d7b71033a9d4f7376da8b0f74630138637dc178a0dd46b4afcf95aa0bc739")
print(tx_hash["from"])
print(tx_hash["to"])
value = w3.from_wei(tx_hash["value"], "ether")
gas = w3.from_wei(tx_hash["gasPrice"], "ether")
print(value)
print(gas)

