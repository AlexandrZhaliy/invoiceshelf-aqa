"""New invoice form"""

from playwright.sync_api import Page


class InvoicePage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.first_row = page.locator("tbody tr").first

    def open_new(self) -> None:
        self.page.goto("/admin/invoices/create")

    def choose_customer(self, name: str) -> None:
        self.page.get_by_role("button", name="New Customer").click()
        self.page.get_by_role("textbox", name="Search").last.fill(name)
        self.page.get_by_text(name).first.click()

    def add_catalog_item(self, item_name: str, quantity: int) -> None:
        """The item comes from the catalog; its price is filled in by the form."""
        row_select = self.first_row.locator("input[type='text']").first
        row_select.click()
        row_select.fill(item_name)
        self.page.locator("li").filter(has_text=item_name).first.click()
        self.first_row.locator("input[type='number']").fill(str(quantity))

    def save(self) -> None:
        self.page.get_by_role("button", name="Save Invoice").click()
