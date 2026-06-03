from playwright.sync_api import sync_playwright

def get_listings():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            permissions=[],  # забороняємо геолокацію
            geolocation=None
        )
        page = context.new_page()
        page.goto("https://www.olx.pl/nieruchomosci/mieszkania/wynajem/lublin/", wait_until="domcontentloaded")
        page.get_by_role("button", name="Akceptuj niezbędne").click()
        room_num = page.locator("[data-testid='multi-select-filter']").filter(has_text="pokoi")
        room_num.locator("[data-testid='dropdown-head']").click()
        page.get_by_role("option", name="3 pokoje").click()
        page.get_by_role("option", name="4 i więcej").click()
        page.get_by_placeholder("Do").nth(0).fill("2500")
        page.locator("[data-testid='search-submit']").click()
        page.locator("[data-testid='sorting-wrapper']").click()
        page.locator("[title='Najnowsze']").click()
        page.wait_for_timeout(2000)
        page.wait_for_selector("[data-testid='l-card']")
        all_listings = page.locator("[data-testid='l-card']").all()
        scraped_data = []
        for listing in all_listings:
            try:
                title = listing.locator("[data-testid='ad-card-title']").text_content()
                price = listing.locator("[data-testid='ad-price']").text_content()
                link_raw = listing.locator("a").first.get_attribute("href")
                link = f"https://www.olx.pl{link_raw}" if link_raw.startswith("/") else link_raw
                link = link.split("?")[0].split("#")[0]
                scraped_data.append({
                    "title": title,
                    "price": price,
                    "link": link
                })
            except:
                continue
        return scraped_data

