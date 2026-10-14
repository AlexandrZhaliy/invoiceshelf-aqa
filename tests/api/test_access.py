"""Access control: a user whose role only allows viewing catalog items must not get at company data.
Invoice ids are sequential integers issued by the application, so a neighbouring id is easy to guess.
The tests below check that guessing an id gives nothing without the correct permission
"""

import allure
import pytest
from framework.api.invoices import InvoicesApi


pytestmark = [pytest.mark.api]

@allure.feature("Access control")
class TestAccessControl:
    def test_user_without_permissions_cannot_list_invoices(self, limited_api):
        response = InvoicesApi(limited_api).list()
        assert response.status_code == 403, response.text

    def test_user_without_permissions_cannot_read_invoice_by_id(self, invoices_api, limited_api, invoice):
        # Control: the invoice exists and the admin can read it, so the refusal below is exactly about permissions
        assert invoices_api.get(invoice["id"]).status_code == 200

        response = InvoicesApi(limited_api).get(invoice["id"])
        assert response.status_code in (403, 404), response.text