"""New customer form"""

from playwright.sync_api import Page


class CustomerPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def open_new(self) -> None:
        self.page.goto("/admin/customers/create")

    def fill_name(self, name: str) -> None:
        # Name is the only required field. .first: the billing and shipping blocks below have a "name" input too
        self.page.locator("input[name='name']").first.fill(name)

    def save(self) -> None:
        self.page.get_by_role("button", name="Save Customer").click()