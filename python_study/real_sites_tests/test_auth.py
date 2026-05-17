from playwright.sync_api import sync_playwright, expect
from python_study.playwright_components.login_page import LoginPage


def test_successful_login():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        login_page = LoginPage(page)
        login_page.navigate()
        login_page.login("tomsmith","SuperSecretPassword!")
        expect(login_page.flash_message).to_contain_text("You logged into")
        browser.close()