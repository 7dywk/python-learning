import pytest
from playwright.sync_api import expect

@pytest.fixture
def login_page(page):
    page.goto("https://the-internet.herokuapp.com/login")
    return page


def test_login(login_page):
    login_page.locator("[id='[username]']").fill("tomsmith")
    login_page.locator("[id='password']").fill("SuperSecretPassword!")
    login_page.get_by_role("button", name="Login").click()
    expect(login_page).to_have_url("https://the-internet.herokuapp.com/secure")


def test_invalid_username(login_page):
    login_page.locator("[id='username']").fill("tomsmit")
    login_page.locator("[id='password']").fill("SuperSecretPassword!")
    login_page.get_by_role("button", name="Login").click()
    expect(login_page.locator("#flash")).to_contain_text('Your username is invalid!')


def test_invalid_password(login_page):
    login_page.locator("[id='username']").fill("tomsmith")
    login_page.locator("[id='password']").fill("wrongpassword")
    login_page.get_by_role("button", name="Login").click()
    expect(login_page.locator("#flash")).to_contain_text('Your password is invalid!')