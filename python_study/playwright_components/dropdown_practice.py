import pytest
from playwright.sync_api import expect


@pytest.fixture
def dd_page(page):
    page.goto("https://the-internet.herokuapp.com/dropdown")
    return page


@pytest.mark.parametrize("option_value", ["1", "2"])
def test_dd(dd_page,option_value):
    dd_page.locator("#dropdown").select_option(option_value)
    expect(dd_page.locator("#dropdown")).to_have_value(option_value)


