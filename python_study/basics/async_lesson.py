# import asyncio
# import random
# import os
# import certifi
# from web3 import AsyncWeb3
#
# os.environ['SSL_CERT_FILE'] = certifi.where()
# os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
#
#
# class CryptoChecker:
#     def __init__(self, rpc: str):
#         # 1. Підключаємось до блокчейну лише ОДИН раз при створенні об'єкта
#         self.w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(rpc))
#
#     # 2. Асинхронний метод, який робить одну перевірку
#     async def check_random_wallet(self):
#         # Створюємо випадковий гаманець
#         account = self.w3.eth.account.create(extra_entropy=str(random.randint(1, 999_999_999)))
#
#         # Йдемо в інтернет за балансом (ось тут потрібен await!)
#         balance = await self.w3.eth.get_balance(account=account.address)
#
#         print(f"Гаманець: {account.address} | Баланс: {balance}")
#         return balance
#
#
# # 3. Головна функція
# async def main():
#     # Створюємо нашого "перевіряльника" ОДИН раз (двері відкриті)
#     checker = CryptoChecker(rpc='https://arb-one.api.pocket.network')
#
#     while True:
#         print("\n--- Запускаємо пачку з 5 гаманців одночасно ---")
#
#         # TODO для тебе:
#         # Нам треба запустити метод checker.check_random_wallet() 5 разів ОДНОЧАСНО.
#         # Для цього в asyncio є чарівна функція asyncio.gather()
#         # Вона приймає всередину себе виклики функцій і запускає їх паралельно.
#         results = await asyncio.gather(
#             checker.check_random_wallet(),
#             checker.check_random_wallet(),
#             checker.check_random_wallet(),
#             checker.check_random_wallet(),
#             checker.check_random_wallet(),
#         )
#         # Спробуй написати тут код, який використовує asyncio.gather
#         # Підказка: це виглядатиме приблизно так:
#         # results = await asyncio.gather(виклик_1, виклик_2, ...)
#         for result in results:
#             if result > 0:
#                 print(f'Wallet with money')
#                 break
#         # А далі, якщо в результатах (results) є число більше нуля - зупиняємо цикл (break)
#         await asyncio.sleep(2)  # Пауза на 2 секунди між пачками, щоб сервер нас не забанив
#
#
# if __name__ == '__main__':
#     asyncio.run(main())

import asyncio
import random

from web3 import AsyncWeb3


class CryptoChecker:
    def __init__(self, rpc: str):
        self.w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(rpc))

    # Метод ТІЛЬКИ для походу в інтернет за балансом
    async def get_balance(self, address: str):
        return await self.w3.eth.get_balance(account=address)


# --- 1. ВИРОБНИК (Генерує гаманці і кидає в чергу) ---
async def wallet_generator(queue: asyncio.Queue, checker: CryptoChecker):
    print("🚀 Генератор запущено! Починаємо створювати гаманці...")
    while True:
        # Створюємо гаманець
        account = checker.w3.eth.account.create(extra_entropy=str(random.randint(1, 999_999_999)))

        # Кладемо адресу в чергу (await, бо якщо черга переповнена - він трохи зачекає)
        await queue.put(account.address)

        # Мікропауза, щоб не згенерувати мільйон гаманців за секунду і не "повісити" комп'ютер
        await asyncio.sleep(0.01)


# --- 2. ВОРКЕР/СПОЖИВАЧ (Бере з черги і перевіряє) ---
async def worker(worker_id: int, queue: asyncio.Queue, checker: CryptoChecker):
    print(f"👷 Воркер {worker_id} готовий до роботи!")
    while True:
        # Чекаємо, поки в черзі з'явиться гаманець, і забираємо його
        address = await queue.get()

        # Йдемо перевіряти баланс (Ось тут займає час!)
        balance = await checker.get_balance(address)

        if balance > 0:
            print(f"\n💰 ВОРКЕР {worker_id} ЗНАЙШОВ ГРОШІ! Гаманець: {address} | Баланс: {balance}")
            # Оскільки процеси фонові, найнадійніший спосіб їх вбити - жорсткий вихід
            os._exit(0)
        else:
            print(f"Address {address} - 0.")

        # Кажемо черзі: "Я закінчив з цією задачею, давай наступну"
        queue.task_done()


# --- 3. ГОЛОВНА ФУНКЦІЯ (Оркестратор) ---
async def main():
    checker = CryptoChecker(rpc='https://arb-one.api.pocket.network')

    # Створюємо чергу (кошик). maxsize=100 означає, що генератор зупиниться,
    # якщо на столі вже лежить 100 неперевірених гаманців.
    queue = asyncio.Queue(maxsize=100)

    # Створюємо 5 воркерів і відправляємо їх працювати У ФОН (create_task)
    for i in range(1, 25):
        asyncio.create_task(worker(i, queue, checker))

    # Запускаємо генератор (він працюватиме нескінченно в головному потоці)
    await wallet_generator(queue, checker)


if __name__ == '__main__':
    asyncio.run(main())