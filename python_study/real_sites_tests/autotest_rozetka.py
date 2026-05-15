# import asyncio
# from playwright.async_api import async_playwright, expect
# from playwright_stealth import Stealth
#
# def clean_price(price_text):
#     clean_string = price_text.replace("&nbsp;", "").replace(" ", "")
#     return int(clean_string)


# async def attempt_1():
#     async with Stealth().use_async(async_playwright()) as p:
#         browser = await p.chromium.launch(headless=False)
#         page = await browser.new_page()
#         print("Opening page")
#         await page.goto("https://epicentrk.ua/")
#         search_field = page.locator("[data-testid='search-suggest-input']")
#         search_button = page.locator("[data-testid='search-suggest-submit']")
#         await search_field.click()
#         await search_field.press_sequentially("Iphone 17 pro max", delay=100)
#         await search_button.click()
#         search_header = page.locator('h1')
#         await expect(search_header).to_contain_text("Iphone", ignore_case=True, timeout=10000)
#         print(f"Right page was opened")
#         product_names = page.locator('.title-title.black-link.text-base')
#         await product_names.first.click()
#         search_header = page.locator('h1')
#         await expect(search_header).to_contain_text("Iphone 17 pro max", ignore_case=True)
#         print(f"Right product was found")
#         await page.locator('.buy-button').first.click()
#         await page.locator('[data-testid="continue-shopping-link"]').click()
#         await search_field.click()
#         await search_field.clear()
#         await search_field.press_sequentially("Велосипед", delay=100)
#         await search_button.click()
#         search_header = page.locator('h1')
#         await expect(search_header).to_contain_text("Велосипед", ignore_case=True, timeout=10000)
#         print(f"Right page was opened for second product")
#         await page.locator("[id='sort']").select_option("expensive")
#         prices = page.locator('.goods-tile__price-value')
#         price1_raw = await prices.nth(0).inner_text()
#         price2_raw = await prices.nth(1).inner_text()
#         p1 = clean_price(price1_raw)
#         p2 = clean_price(price2_raw)
#         print(f"First price is {p1} and second is {p2}")
#         assert p1 >= p2, f"❌ Сортування зламалося! Перша ціна {p1} більша за другу {p2}"
#         product2_names = page.locator('.goods-tile__title')
#         await product2_names.first.click()
#         await expect(page).to_have_url("https://rozetka.com.ua/ua/bottecchia-8057461252341/p581074765/")
#         print(f"Second product was found correctly")
#         await page.locator(".buy-button").first.click()
#         cart_header = page.locator('h2')
#         await expect(cart_header).to_contain_text("Кошик", ignore_case=True)
#         print(f"Product was added to cart")
#
#
# if __name__ == "__main__":
#     asyncio.run(attempt_1())


# ... твої імпорти та функція clean_price ...
import asyncio
from playwright.async_api import async_playwright, expect
from playwright_stealth import Stealth


def clean_price(price_text):
    # Додав сюди '₴' та 'грн' про всяк випадок, бо магазини люблять їх ліпити до цифр
    clean_string = str(price_text).replace("&nbsp;", "").replace("\xa0", "").replace(" ", "").replace("₴", "").replace(
        "грн", "")
    return int(clean_string)


async def attempt_1():
    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(permissions=['geolocation'])

        # 2. Створюємо сторінку вже з цього налаштованого контексту!
        page = await context.new_page()

        print("Відкриваємо Epicentr...")
        await page.goto("https://epicentrk.ua/")

        # Закриваємо банер
        await page.get_by_role("button", name="Відхилити").click()

        # --- ТОВАР 1: ВЕЛОСИПЕД ---
        print("Шукаємо велосипед...")
        search_field = page.get_by_role("searchbox", name="Пошук")
        await search_field.click()
        await search_field.fill("Велосипед")
        await search_field.press("Enter")

        # Чекаємо заголовок, щоб переконатися, що пошук спрацював
        search_header = page.locator('h1', has_text="Велосипед")

        # 2. Тепер нам не треба перевіряти текст через expect,
        # нам треба просто почекати, поки цей знайдений заголовок стане ВИДИМИМ
        await expect(search_header).to_be_visible(timeout=10000)

        print("Сортуємо велосипеди (найдорожчі)...")
        await page.get_by_text("дорогі", exact=True).click()
        await page.wait_for_timeout(2000)  # Даємо сайту секунду на перемальовування списку

        # ПЕРЕВІРКА ЦІН
        # УВАГА: Оскільки ти не клікав по цінах у codegen, я використав загальний селектор карток.
        # Якщо впаде на цьому місці, перевір клас ціни через Inspect (можливо там щось типу .p-price__main)
        prices = page.locator('[itemprop="price"]')  # Приблизні класи Епіцентру

        price1_raw = await prices.nth(0).inner_text()
        price2_raw = await prices.nth(1).inner_text()
        p1 = clean_price(price1_raw)
        p2 = clean_price(price2_raw)

        print(f"Перша ціна: {p1}, Друга ціна: {p2}")
        # Оскільки сортування "дорогі", перша має бути БІЛЬШОЮ або рівною
        assert p1 >= p2, f"❌ Сортування зламалося! Перша ціна {p1} менша за другу {p2}"

        print("Клікаємо на найдорожчий велосипед...")
        # Шукаємо всі посилання, всередині яких є фото або назва, і клікаємо на перше
        # Шукаємо всі елементи, які мають цей атрибут, і клікаємо на перший
        await page.locator('[data-product-picture]').first.click()

        print("Додаємо велосипед у кошик...")
        await page.locator("#main").get_by_role("button", name="Купити").click()
        await page.get_by_role("button", name="Продовжити покупки").click()

        # --- ТОВАР 2: ГЕНЕРАТОР ---
        print("Шукаємо генератор...")
        # Поле пошуку на інших сторінках може втратити фокус, тому знаходимо його знову
        search_field_2 = page.get_by_role("searchbox", name="Пошук")
        await search_field_2.click()
        await search_field_2.clear()  # Очищаємо попередній запит
        await search_field_2.fill("Генератор")
        await search_field_2.press("Enter")

        search_header_2 = page.locator('h1', has_text="Генератор")
        await expect(search_header_2).to_be_visible(timeout=10000)

        print("Сортуємо генератори (дешевші)...")
        await page.get_by_role("link", name="дешевші").click()
        await page.wait_for_timeout(2000)

        print("Клікаємо на найдешевший генератор...")
        # Шукаємо всі елементи, які мають цей атрибут, і клікаємо на перший
        await page.locator('[data-product-picture]').first.click()

        print("Додаємо генератор у кошик...")
        await page.locator("#main").get_by_role("button", name="Купити").click()


        print("✅ Успіх! Обидва товари в кошику.")


if __name__ == "__main__":
    asyncio.run(attempt_1())

