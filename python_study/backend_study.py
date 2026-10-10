import asyncio
import websockets
import json


trade_queue = asyncio.Queue()
async def stream_price(symbol):
    url = f"wss://stream.binance.com:9443/ws/{symbol}@bookTicker"
    while True:
        try:
            async with websockets.connect(url) as ws:
                while True:
                    message = await ws.recv()
                    data = json.loads(message)
                    bid = float(data["b"])
                    ask = float(data["a"])
                    await trade_queue.put({"symbol": symbol, "bid": bid, "ask": ask})
        except Exception as e:
            print(f'error:{e} reconnection in 2 seconds')
            await asyncio.sleep(2)




async def analyzer():
    while True:
        trade = await trade_queue.get()
        spread = trade["ask"] - trade["bid"]
        print(f'{trade["symbol"].upper()} | Bid: {trade["bid"]} | Ask: {trade["ask"]} | Spread: {spread:.4f}')



async def main():
    await asyncio.gather(
        # stream_price("btcusdt"),
        stream_price("ethusdt"),
        analyzer(),
    )

asyncio.run(main())
