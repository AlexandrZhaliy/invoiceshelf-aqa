"""Login page. Page objects only act; assertions stay in tests"""

from playwright.sync_api import Page


class LoginPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self) -> None:
        self.page.goto("/login")

    def log_in(self, email: str, password: str) -> None:
        self.page.locator("input[name='email']").fill(email)
        self.page.locator("input[name='password']").fill(password)
        self.page.get_by_role("button", name="Login").click()


