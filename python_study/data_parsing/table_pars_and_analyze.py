from playwright.sync_api import sync_playwright

def due_check(page):
    page.goto("https://the-internet.herokuapp.com/tables")
    rows = page.locator("table#table1 tbody tr").all()
    values = []

    for row in rows:
        name = row.locator("td").nth(1).text_content()
        due =  row.locator("td").nth(3).text_content()
        values.append((name, float(due.replace("$", ""))))

    return max(values, key=lambda x: x[1])


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    result = due_check(page)
    print(result)
    browser.close()