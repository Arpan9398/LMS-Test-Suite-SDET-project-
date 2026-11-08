"""Base page object with helpers shared by every page."""
from playwright.sync_api import Page


class BasePage:
    path = "/"

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def open(self):
        self.page.goto(f"{self.base_url}{self.path}")
        return self

    def by_id(self, test_id: str):
        """Locator by data-testid (Playwright's default test-id attribute)."""
        return self.page.get_by_test_id(test_id)

    def logout(self):
        self.by_id("logout-link").click()
