import os
import requests
import time
from web3 import Web3
from dotenv import load_dotenv


load_dotenv()

rpc_url = os.getenv("ANKR_RPC_URL")
bot_token = os.getenv("TG_BOT_TOKEN")
chat_id = os.getenv("TG_CHAT_ID")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"❌ Telegram API Error: {response.text}")
    except Exception as e:
        print(f"Unable to send message: {e}")


w3 = Web3(Web3.HTTPProvider(rpc_url))

abi = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "sender", "type": "address"},
            {"indexed": True, "name": "recipient", "type": "address"},
            {"indexed": False, "name": "amount0", "type": "int256"},
            {"indexed": False, "name": "amount1", "type": "int256"},
            {"indexed": False, "name": "sqrtPriceX96", "type": "uint160"},
            {"indexed": False, "name": "liquidity", "type": "uint128"},
            {"indexed": False, "name": "tick", "type": "int24"}
        ],
        "name": "Swap",
        "type": "event"
    }
]

address = w3.to_checksum_address("0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640")


def main():
    contract = w3.eth.contract(address=address, abi=abi)
    last_block = w3.eth.block_number

    while True:
        try:
            current_block = w3.eth.block_number
            if current_block > last_block:
                print(f"Сканую блок {current_block}...")
                logs = contract.events.Swap().get_logs(
                    from_block=last_block + 1,
                    to_block=current_block,
                )
                for log in logs:
                    args = log["args"]
                    eth_amount = abs(args["amount1"]) / 10 ** 18

                    if eth_amount > 10:
                        sender = w3.eth.get_transaction(log["transactionHash"])["from"]

                        if args["amount1"] < 0:
                            msg = f"*Swap Alert!* \nАдреса: `{sender}`\nКупив: {eth_amount:.4f} ETH"
                        else:
                            msg = f"*Swap Alert!* \nАдреса: `{sender}`\nПродав: {eth_amount:.4f} ETH"

                        print(msg)
                        send_telegram_message(msg)
                last_block = current_block
        except Exception as e:
            print(f"Network error: {e}")
        time.sleep(12)


if __name__ == "__main__":
    main()