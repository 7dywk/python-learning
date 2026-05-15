from playwright.sync_api import expect


def test_load(page):
    page.goto("https://the-internet.herokuapp.com/dynamic_loading/1")
    page.get_by_role("button", name="Start").click()
    page.locator("#finish").wait_for(state="visible")
    expect(page.locator("#finish")).to_be_visible()