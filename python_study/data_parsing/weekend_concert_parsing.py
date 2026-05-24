import pandas as pd
from playwright.sync_api import sync_playwright


def clean_price(unclean_price):
    cleaned_price = unclean_price.replace("zł", "").replace("za jeden bilet", "")
    cleaned_price = cleaned_price.replace(" ", "").replace("\xa0", "")
    cleaned_price = cleaned_price.replace(",", ".")
    return float(cleaned_price)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.alebilet.pl/bilety/the-weeknd/2026-08-05/17:00/after-hours-til-dawn-tour")
    page.wait_for_selector(".cat")
    ticket_list = page.locator("table#ticket-list tbody tr").all()
    scraped_data = []
    for ticket in ticket_list:
        raw_sector = ticket.locator("span.cat").first.text_content().strip()
        clean_sector = raw_sector.split('\n')[0].replace('\xa0', ' ').strip()
        price_text = ticket.locator("td.price").text_content().strip()
        price = clean_price(price_text)
        ticket_info = {
            "sector": clean_sector,
            "price": price,
        }

        scraped_data.append(ticket_info)
for data in scraped_data:
    print(data)


print("Дані зібрано! Передаємо їх у Pandas...")
df = pd.DataFrame(scraped_data)
cheap_tickets_df = df[df['price'] < 1000]
cheap_tickets_df.to_csv("../test_data/cheap_tickets.csv", index=False, encoding="utf-8-sig")

print(f"Готово! Знайдено {len(cheap_tickets_df)} дешевих квитків. Файл збережено.")