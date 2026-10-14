import re
import allure
import pytest
from playwright.sync_api import expect
from framework.ui.base import entity_id
from framework.ui.invoice_page import InvoicePage

pytestmark = [pytest.mark.ui]


@allure.feature("Invoices")
def test_create_invoice_through_the_form(admin_page, customer, catalog_item, invoices_api, cleanup):
    """Customer and catalog item are prepared through the API: the test is about the invoice form only."""
    form = InvoicePage(admin_page)
    form.open_new()
    form.choose_customer(customer["name"])
    form.add_catalog_item(catalog_item["name"], quantity=2)
    form.save()

    expect(admin_page).to_have_url(re.compile(r"/admin/invoices/\d+/view$"))
    invoice_id = entity_id(admin_page)
    cleanup(lambda: invoices_api.delete(invoice_id))

    stored = invoices_api.get(invoice_id).json()["data"]
    assert stored["customer"]["id"] == customer["id"]
    assert stored["total"] == 10000  # 2 x 50.00
    assert stored["status"] == "DRAFT"
    assert stored["paid_status"] == "UNPAID"