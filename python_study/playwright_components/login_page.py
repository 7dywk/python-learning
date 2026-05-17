class LoginPage:
    def __init__(self, page):
        self.page = page
        self.username_field = self.page.locator("#username")
        self.password_field = self.page.locator("#password")
        self.login_button = self.page.locator("button.radius")
        self.flash_message = self.page.locator("#flash")


    def navigate(self):
        self.page.goto("https://the-internet.herokuapp.com/login")


    def login(self, username, password):
        self.username_field.fill(username)
        self.password_field.fill(password)
        self.login_button.click()


