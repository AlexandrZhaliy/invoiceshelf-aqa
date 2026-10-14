"""New payment form. The amount is typed in currency units (30.00), unlike the API, which uses minor units"""

from playwright.sync_api import Page, expect
from framework.ui.base import field, pick


class PaymentPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def open_new(self) -> None:
        self.page.goto("/admin/payments/create")
        # The form fills in the next payment number once its data is loaded: wait for it before touching dropdowns
        expect(field(self.page, "Payment Number").locator("input")).not_to_have_value("")

    def choose_customer(self, name: str) -> None:
        pick(self.page, field(self.page, "Customer"), name)

    def choose_invoice(self, invoice_number: str) -> None:
        pick(self.page, field(self.page, "Invoice"), invoice_number)

    def set_amount(self, amount: str) -> None:
        field(self.page, "Amount").locator("input").fill(amount)

    def choose_payment_mode(self, mode: str) -> None:
        pick(self.page, field(self.page, "Payment Mode"), mode)

    def save(self) -> None:
        self.page.get_by_role("button", name="Save Payment").click()

