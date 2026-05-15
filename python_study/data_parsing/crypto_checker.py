import requests
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

api_token = "8631133833:AAEjOUKOSonSjQvK2VHoUFr86amdgar009g"
bot = Bot(token = api_token )
dp = Dispatcher()


def get_bybit_price(symbol):
    url = f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}"
    response = requests.get(url)
    status = response.status_code
    if status == 200:
        data = response.json()
        if len(data['result']) == 0:
            print(f"Bybit: Монету {symbol} не знайдено!")
            return None
    elif status == 404:
        print("wrong info")
        return None
    else:
        print(f"unknown error{status}")
        return None
    price_str = data['result']['list'][0]['lastPrice']
    price_float = float(price_str)
    return price_float


def get_okx_price(symbol):
    okx_symbol = symbol.replace("USDT", "-USDT")
    url = f"https://www.okx.com/api/v5/market/ticker?instId={okx_symbol}"
    response = requests.get(url)
    status = response.status_code
    if status == 200:
        data = response.json()
        if len(data['data']) == 0:
            print(f"OKX: Монету {symbol} не знайдено!")
            return None
        price_str = data['data'][0]['last']
        price_float = float(price_str)
        return price_float
    elif status == 404:
        print("wrong info")
        return None
    else:
        print(f"unknown error{status}")
        return None


def get_binance_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url)
    status = response.status_code
    if status == 200:
        data = response.json()
        price_str = data['price']
        price_float = float(price_str)
        return price_float
    elif status == 400:
        print(f"Binance: Монету {symbol} не знайдено!")
        return None
    elif status == 404:
        print("wrong info")
        return None
    else:
        print(f"unknown error{status}")
        return None


def get_gate_price (symbol):
    gate_symbol = symbol.replace("USDT", "_USDT").upper()
    url = f"https://api.gateio.ws/api/v4/spot/tickers?currency_pair={gate_symbol}"
    response = requests.get(url)
    status = response.status_code
    if status == 200:
        data = response.json()
        price_str = data[0]['last']
        price_float = float(price_str)
        return price_float
    elif status == 400:
        print(f"Gate: Монету {symbol} не знайдено!")
        return None
    elif status == 404:
        print("wrong info")
        return None
    else:
        print(f"unknown error{status}")
        return None


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Напиши монету (Приклад: btcusdt)")


@dp.message()
async def handle_message(message: types.Message):
    user_symbol = message.text.upper().replace(" ", "")
    await message.answer(f"⏳ Отримую дані для {user_symbol}...")
    bybit_price = get_bybit_price(user_symbol)
    okx_price = get_okx_price(user_symbol)
    binance_price = get_binance_price(user_symbol)
    gate_price = get_gate_price(user_symbol)

    all_prices = {
        "Bybit": bybit_price,
        "OKX": okx_price,
        "Binance": binance_price,
        "Gate": gate_price,
    }

    # Фільтруємо робочі ціни
    valid_prices = {ex: p for ex, p in all_prices.items() if p is not None}

    if not valid_prices:
        await message.answer(f"❌ Монету {user_symbol} не знайдено на жодній біржі.")
        return

    # Формуємо текст відповіді
    text = f"📊 Результати для {user_symbol}:\n" + "-" * 20 + "\n"
    for ex, p in valid_prices.items():
        text += f"🔹 {ex}: {p}\n"

    # Розрахунок спреду (твій код, але адаптований під текст бота)
    if len(valid_prices) >= 2:
        buy_ex = min(valid_prices, key=valid_prices.get)
        sell_ex = max(valid_prices, key=valid_prices.get)

        spread = valid_prices[sell_ex] - valid_prices[buy_ex]
        spread_perc = (spread / valid_prices[buy_ex]) * 100

        text += "-" * 20 + f"\n💰 Спред: {spread:.4f} USD ({spread_perc:.3f}%)\n"
        text += f"🚀 {buy_ex} ➡️ {sell_ex}"
    else:
        text += "\n⚠️ Недостатньо даних для спреду."

    await message.answer(text)


# 2. Фінальна частина — запуск бота
async def main():
    print("Бот запущений і чекає повідомлень...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())




# user_symbol = input("Введи монету (наприклад, BTCUSDT): ").upper()
# print("\nШукаю ціни, зачекай...")
#
# bybit_price = get_bybit_price(user_symbol)
# okx_price = get_okx_price(user_symbol)
# binance_price = get_binance_price(user_symbol)
# gate_price = get_gate_price(user_symbol)
# all_prices = {
#     "Bybit": bybit_price,
#     "OKX": okx_price,
#     "Binance": binance_price,
#     "Gate": gate_price,
# }
#
# valid_prices = {exchange: price for exchange, price in all_prices.items() if price is not None }
# if len(valid_prices) > 0:
#     print("-" * 35)
#     for exchange, price in valid_prices.items():
#         print(f"📊 Ціна на {exchange}: {price}")
#     print("-" * 35)
#
# if len(valid_prices) >= 2:
#
#     buy_exchange = min(valid_prices, key=valid_prices.get)
#     sell_exchange = max(valid_prices, key=valid_prices.get)
#
#     buy_price = valid_prices[buy_exchange]
#     sell_price = valid_prices[sell_exchange]
#
#     spread = sell_price - buy_price
#     spread_percent = (spread / buy_price) * 100
#
#     print(f"💰 Максимальний спред: {spread:.4f} USD ({spread_percent:.3f}%)")
#
#     if spread > 0:
#         print(f"🚀 Купуй на {buy_exchange} -> Продавай на {sell_exchange}!")
#     else:
#         print("⚖️ Ціни абсолютно однакові, спреду немає.")
#
# else:
#     print("❌ Недостатньо даних для розрахунку спреду (монета є менш ніж на двох біржах).")