import re
import allure
import pytest
from playwright.sync_api import expect
from framework.ui.base import entity_id
from framework.ui.invoice_page import InvoicePage
from framework.ui.payment_page import PaymentPage

pytestmark = [pytest.mark.e2e]


@allure.feature("Invoice to payment")
def test_invoice_created_in_ui_is_fully_paid_in_ui(
    admin_page, customer, catalog_item, invoices_api, payments_api, db, cleanup
):
    """The whole business flow as a user lives it: invoice, then payment. Data is prepared through the API
    (customer, catalog item); the result is checked through the API and in the database."""
    # ================ 1. Invoice through the form: 2 x 50.00 = 100.00 =========================
    invoice_form = InvoicePage(admin_page)
    invoice_form.open_new()
    invoice_form.choose_customer(customer["name"])
    invoice_form.add_catalog_item(catalog_item["name"], quantity=2)
    invoice_form.save()

    expect(admin_page).to_have_url(re.compile(r"/admin/invoices/\d+/view$"))
    invoice_id = entity_id(admin_page)

    cleanup(lambda: invoices_api.delete(invoice_id))
    invoice = invoices_api.get(invoice_id).json()["data"]
    assert invoice["total"] == 10000


    # ================ 2. The whole amount through the payment form ============================
    payment_form = PaymentPage(admin_page)
    payment_form.open_new()
    payment_form.choose_customer(customer["name"])
    payment_form.choose_invoice(invoice["invoice_number"])
    payment_form.set_amount("100.00")
    payment_form.choose_payment_mode("Cash")
    payment_form.save()

    expect(admin_page.get_by_text("Payment created successfully")).to_be_visible()
    payments = payments_api.list_payments_by_customer(customer["id"]).json()["data"]
    assert len(payments) == 1

    cleanup(lambda: payments_api.delete(payments[0]["id"]))


    # ============ 3. The result: the invoice is paid, in the API and in the database ==========
    paid = invoices_api.get(invoice_id).json()["data"]
    assert paid["paid_status"] == "PAID"
    assert paid["due_amount"] == 0

    row = db.fetch_one("SELECT SUM(amount) AS paid FROM payments WHERE invoice_id = %s", (invoice_id,))
    assert row["paid"] == 10000


