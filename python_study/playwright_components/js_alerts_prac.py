import pytest
from playwright.sync_api import expect

@pytest.fixture
def js_page(page):
    page.goto("https://the-internet.herokuapp.com/javascript_alerts")
    return page


def test_js_alert(js_page):
    js_page.on("dialog", lambda dialog: dialog.accept())
    js_page.locator('button[onclick="jsAlert()"]').click()
    expect(js_page.locator("#result")).to_have_text("You successfully clicked an alert")


def test_js_confirm_accept(js_page):
    js_page.on("dialog", lambda dialog: dialog.accept())
    js_page.locator('button[onclick="jsConfirm()"]').click()
    expect(js_page.locator("#result")).to_have_text("You clicked: Ok")


def test_js_confirm_dismiss(js_page):
    js_page.on("dialog", lambda dialog: dialog.dismiss())
    js_page.locator('button[onclick="jsConfirm()"]').click()
    expect(js_page.locator("#result")).to_have_text("You clicked: Cancel")


def test_js_prompt_accept(js_page):
    js_page.on("dialog", lambda dialog: dialog.accept())
    js_page.locator('button[onclick="jsPrompt()"]').click()
    expect(js_page.locator("#result")).to_have_text("You entered: ")


def test_js_prompt_text(js_page):
    js_page.on("dialog", lambda dialog: dialog.accept("test"))
    js_page.locator('button[onclick="jsPrompt()"]').click()
    expect(js_page.locator("#result")).to_have_text("You entered: test")


def test_js_prompt_dismiss(js_page):
    js_page.on("dialog", lambda dialog: dialog.dismiss())
    js_page.locator('button[onclick="jsPrompt()"]').click()
    expect(js_page.locator("#result")).to_have_text("You entered: null")