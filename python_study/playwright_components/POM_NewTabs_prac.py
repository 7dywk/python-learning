from playwright.sync_api import expect


class WindowsPage:
    def __init__(self,page):
        self.page = page
        self.click_button = page.locator("a[href='/windows/new']")


    def open_page(self):
        self.page.goto("https://the-internet.herokuapp.com/windows")


    def open_new_tab(self):
        with self.page.context.expect_page() as new_page_info:
            self.click_button.click()

        new_tab = new_page_info.value
        new_tab.wait_for_load_state()
        return new_tab


def test_windows(page):
    windows_page = WindowsPage(page)
    windows_page.open_page()
    new_tab = windows_page.open_new_tab()
    expect(new_tab.locator("h3")).to_have_text("New Window")


