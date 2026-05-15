import pytest
from playwright.sync_api import expect


@pytest.fixture
def login_page(page):
    page.goto("https://the-internet.herokuapp.com/login")
    return page

@pytest.mark.parametrize("username, password, expected",[
    ("tomsmith", "SuperSecretPassword!", "You logged into a secure area!"),
    ("tomsmit", "SuperSecretPassword!", "Your username is invalid!"),
    ("tomsmith", "wrongpassword", "Your password is invalid!"),
])


def test_invalid_password(login_page, username, password, expected):
    login_page.locator("[id='username']").fill(username)
    login_page.locator("[id='password']").fill(password)
    login_page.get_by_role("button", name="Login").click()
    expect(login_page.locator("#flash")).to_contain_text(expected)