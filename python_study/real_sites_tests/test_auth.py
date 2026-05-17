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


def test_wrong_password_login():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        login_page = LoginPage(page)
        login_page.navigate()
        login_page.login("tomsmith","wrong password!")
        expect(login_page.flash_message).to_contain_text("password is invalid")
        browser.close()


def test_wrong_username_login():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        login_page = LoginPage(page)
        login_page.navigate()
        login_page.login("wrong username","SuperSecretPassword!")
        expect(login_page.flash_message).to_contain_text("username is invalid")
        browser.close()