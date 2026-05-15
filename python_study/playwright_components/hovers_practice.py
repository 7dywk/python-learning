import pytest
from playwright.sync_api import expect


@pytest.fixture
def test_page(page):
    page.goto("https://the-internet.herokuapp.com/hovers")
    return page


@pytest.mark.parametrize("index, number",[
    (0,1),
    (1,2),
    (2,3),
])
def test_hover(test_page, index, number):
    test_page.locator(".figure").nth(index).hover()
    expect(test_page.get_by_text(f"name: user{number}")).to_be_visible()
