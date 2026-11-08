from pages.base_page import BasePage


class LoginPage(BasePage):
    path = "/login"

    def login(self, username: str, password: str):
        self.by_id("username").fill(username)
        self.by_id("password").fill(password)
        self.by_id("login-button").click()
        return self

    @property
    def error(self):
        return self.by_id("login-error-message")

    @property
    def welcome(self):
        return self.by_id("welcome")
