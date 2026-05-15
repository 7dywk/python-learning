import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://epicentrk.ua/")
    page.get_by_role("button", name="Відхилити").click()
    page.get_by_role("searchbox", name="Пошук").click()
    page.get_by_role("searchbox", name="Пошук").fill("Велосипед")
    page.get_by_role("searchbox", name="Пошук").press("Enter")
    page.get_by_text("дорогі", exact=True).click()
    page.locator("a").filter(has_text="Велосипед гірський GT ZASKAR").click()
    page.locator("#main").get_by_role("button", name="Купити").click()
    page.get_by_role("button", name="Продовжити покупки").click()
    page.get_by_role("searchbox", name="Пошук").click()
    page.get_by_role("searchbox", name="Пошук").fill("Генератор")
    page.get_by_role("searchbox", name="Пошук").press("Enter")
    page.get_by_role("link", name="дешевші").click()
    page.locator("a").filter(has_text="Генератор бензиновий Vitals").click()
    page.locator("#main").get_by_role("button", name="Купити").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
