# import asyncio
#
# from playwright.async_api import async_playwright
#
# async def main():
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)
#         page = await browser.new_page()
#         await page.goto('https://whatmyuseragent.com/')
#         await page.screenshot(path='./demo.png')
#         await browser.close()
#
#
# if __name__ == '__main__':
#     asyncio.run(main())


# import asyncio
# from playwright.async_api import async_playwright, expect
#
# async def login_test():
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False, slow_mo=500)
#         page = await browser.new_page()
#
#         print("Opening page ")
#
#         await page.goto("https://www.saucedemo.com/")
#         await page.locator('[data-test="username"]').fill("standard_user")
#         await page.locator('[data-test="password"]').fill("secret_sauce")
#         await page.locator('[data-test="login-button"]').click()
#
#
#         print("🔍 Перевіряємо надійні маркери успішного входу...")
#
#         # 1. Перевіряємо URL
#         await expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
#
#         # 2. Перевіряємо видимість кошика
#         cart_icon = page.locator('[data-test="shopping-cart-link"]')
#         await expect(cart_icon).to_be_visible()
#
#         print("✅ Тест пройдено! Ми точно всередині.")
#         await browser.close()
#
# if __name__ == '__main__':
#     asyncio.run(login_test())


# import asyncio
# from playwright.async_api import async_playwright, expect
#
#
# async def invalid_login():
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False, slow_mo=500)
#         page = await browser.new_page()
#
#         print("⏳ Відкриваємо сторінку...")
#         await page.goto("https://www.saucedemo.com/")
#
#         print("✍️ Вводимо правильний логін, але НЕПРАВИЛЬНИЙ пароль...")
#         # TODO 1: Введи логін 'standard_user' (ти вже знаєш як)
#         await page.locator("[data-test='username']").fill("wrong_name")
#         # TODO 2: Введи будь-який неправильний пароль, наприклад 'wrong_pass'
#         await page.locator("[data-test='password']").fill('wrong_password')
#         # TODO 3: Клікни кнопку Login
#         await page.locator("[data-test='login-button']").click()
#         print("🔍 Перевіряємо, чи спрацював захист...")
#
#         # TODO 4: Зайди на сайт руками, введи неправильний пароль і через "Inspect"
#         # знайди, який атрибут data-test має червона плашка з помилкою, що з'явиться.
#         # Підстав цей атрибут сюди замість ХХХ:
#         error_message = page.locator('[data-test="error"]')
#
#         # 1-ша перевірка: Елемент помилки взагалі з'явився на екрані
#         await expect(error_message).to_be_visible()
#
#         # 2-га перевірка: Текст помилки містить слово "sadface" (там завжди є ця фраза)
#         await expect(error_message).to_contain_text("sadface")
#
#         print("✅ Негативний тест пройдено! Система не пустила чужинця і видала правильну помилку.")
#
#         await browser.close()
#
#
# if __name__ == '__main__':
#     asyncio.run(invalid_login())


# import asyncio
# from playwright.async_api import async_playwright, expect
#
#
# async def names_parsing():
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)
#         page = await browser.new_page()
#
#         print("⏳ Відкриваємо сторінку...")
#         await page.goto("https://www.saucedemo.com/")
#         await page.locator("[data-test='username']").fill("standard_user")
#         await page.locator('[data-test="password"]').fill("secret_sauce")
#         await page.locator('[data-test="login-button"]').click()
#         names = page.locator("[data-test='inventory-item-name']")
#         names_list = await names.all_inner_texts()
#         for name in names_list:
#             print(name)
#
#
# if __name__ == "__main__":
#     asyncio.run(names_parsing())


# import asyncio
# from playwright.async_api import async_playwright, expect
#
#
# async def names_price_parsing():
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)
#         page = await browser.new_page()
#
#         print("⏳ Відкриваємо сторінку...")
#         await page.goto("https://www.saucedemo.com/")
#         await page.locator("[data-test='username']").fill("standard_user")
#         await page.locator('[data-test="password"]').fill("secret_sauce")
#         await page.locator('[data-test="login-button"]').click()
#         names = page.locator("[data-test='inventory-item-name']")
#         names_list = await names.all_inner_texts()
#         prices = page.locator("[data-test='inventory-item-price']")
#         prices_list = await prices.all_inner_texts()
#         for name,price in zip(names_list,prices_list):
#             print(f"{name}: {price}")
#
#
#
#
#
# if __name__ == "__main__":
#     asyncio.run(names_price_parsing())


import asyncio
from playwright.async_api import async_playwright, expect


async def low_high_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("⏳ Відкриваємо сторінку...")
        await page.goto("https://www.saucedemo.com/")
        await page.locator("[data-test='username']").fill("standard_user")
        await page.locator('[data-test="password"]').fill("secret_sauce")
        await page.locator('[data-test="login-button"]').click()
        await page.locator('[data-test="product-sort-container"]').select_option("lohi")
        prices = page.locator("[data-test='inventory-item-price']")
        prices_list = await prices.all_inner_texts()
        prices_numbers = [float(price.replace('$', '')) for price in prices_list]
        assert prices_numbers == sorted(prices_numbers), "Error, sorting is broken"



if __name__ == '__main__':
    asyncio.run(low_high_test())