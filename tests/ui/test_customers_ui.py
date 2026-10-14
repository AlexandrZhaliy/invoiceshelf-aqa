import re
import allure
import pytest
from playwright.sync_api import expect
from framework.data.factories import customer_payload
from framework.ui.base import entity_id
from framework.ui.customer_page import CustomerPage

pytestmark = [pytest.mark.ui]


@allure.feature("Customers")
def test_create_customer_through_the_form(admin_page, customers_api, cleanup):
    name = customer_payload()["name"]

    form = CustomerPage(admin_page)
    form.open_new()
    form.fill_name(name)
    form.save()

    expect(admin_page).to_have_url(re.compile(r"/admin/customers/\d+/view$"))
    customer_id = entity_id(admin_page)
    cleanup(lambda: customers_api.delete(customer_id))

    # The customer really exists with the name typed into the form
    stored = customers_api.get(customer_id).json()["data"]
    assert stored["name"] == name
