import asyncio
import time
# async def download_logs(server_name, delay):
#     print(f'Connecting to sever {server_name} ')
#     await asyncio.sleep(delay)
#     print(f'Logs successfully downloaded to {server_name}')
#
#
# async def main():
#     t1 = time.time()
#     await asyncio.gather(
#         download_logs('Alpha', 7),
#         download_logs('Beta', 2),
#         download_logs('Gamma', 3),
#     )
#     t2 = time.time()
#     print(f'Downloaded logs in {t2 - t1:.2f} seconds')
#
#
# if __name__ == '__main__':
#     asyncio.run(main())


async def check_api(endpoint, delay, is_broken=False):
    await asyncio.sleep(delay)
    if is_broken:
        raise TimeoutError(f"Сервер {endpoint} не відповів!")
    else:
        return f"{endpoint}: status 200"


async def main():
    t1 = time.time()
    results = await asyncio.gather(
        check_api('/login', 1, is_broken=False),
        check_api('/cart', 2, is_broken=True),
        check_api('/checkout', 1.5, is_broken=False),
        return_exceptions=True,
    )
    t2 = time.time()
    for result in results:
        if isinstance(result, Exception):
            print(f"❌ ТЕСТ ВПАВ! Причина: {result}")
        else:
            print(f"✅ ТЕСТ ПРОЙШОВ: {result}")
    print(f"Time taken: {t2 - t1:.2f}") 


if __name__ == '__main__':
    asyncio.run(main())


