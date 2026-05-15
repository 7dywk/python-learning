import pytest
from playwright.sync_api import expect

@pytest.fixture
def checkbox_page(page):
    page.goto("https://the-internet.herokuapp.com/checkboxes")
    return page


@pytest.mark.parametrize("index", [0, 1])
def test_checkbox(checkbox_page, index):
    first_checkbox = checkbox_page.locator("[type='checkbox']").nth(index)
    first_checkbox.check()
    expect(first_checkbox).to_be_checked()

@pytest.mark.parametrize("index", [0, 1])
def test_uncheck(checkbox_page,index):
    checkbox = checkbox_page.locator("[type='checkbox']").nth(index)
    checkbox.uncheck()
    expect(checkbox).not_to_be_checked()


def test_two_checkboxes(checkbox_page):
    checkbox = checkbox_page.locator("[type='checkbox']")
    checkbox.nth(0).check()
    checkbox.nth(1).check()
    expect(checkbox.nth(0)).to_be_checked()
    expect(checkbox.nth(1)).to_be_checked()


