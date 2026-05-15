from playwright.sync_api import sync_playwright


def parsing_table(page):
    page.goto("https://the-internet.herokuapp.com/tables")
    rows = page.locator("table#table1 tbody tr")

    for i in range(rows.count()):
        row = rows.nth(i)
        cells = row.locator("td")

        last_name = cells.nth(0).inner_text()
        first_name = cells.nth(1).inner_text()
        due = cells.nth(3).inner_text()

        print(f"Клієнт: {first_name} {last_name} | Борг: {due}")


# Точка входу в звичайний скрипт
with sync_playwright() as p:
    # Відкриваємо браузер (headless=False, щоб бачити, що відбувається)
    browser = p.chromium.launch()
    page = browser.new_page()

    # ТЕПЕР ми викликаємо нашу функцію і передаємо їй створену сторінку
    parsing_table(page)

    browser.close()