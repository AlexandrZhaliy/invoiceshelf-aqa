import allure
import pytest
from playwright.sync_api import expect
from framework.ui.payment_page import PaymentPage

pytestmark = [pytest.mark.ui]


@allure.feature("Payments")
def test_record_payment_through_the_form(admin_page, customer, invoice, invoices_api, payments_api, cleanup):
    """The invoice (100.00 in total) is prepared through the API. The form takes the amount in currency units."""
    form = PaymentPage(admin_page)
    form.open_new()
    form.choose_customer(customer["name"])
    form.choose_invoice(invoice["invoice_number"])
    form.set_amount("30.00")
    form.choose_payment_mode("Cash")
    form.save()

    expect(admin_page.get_by_text("Payment created successfully")).to_be_visible()

    # The new payment is found by its customer: the customer is unique to this test
    payments = payments_api.list_payments_by_customer(customer["id"]).json()["data"]
    assert len(payments) == 1   # the only current payment should exist, no doubles expected
    cleanup(lambda: payments_api.delete(payments[0]["id"]))
    assert payments[0]["amount"] == 3000  # the API counts in minor units

    stored = invoices_api.get(invoice["id"]).json()["data"]
    assert stored["paid_status"] == "PARTIALLY_PAID"
    assert stored["due_amount"] == 7000
