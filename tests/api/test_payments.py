"""Payment API tests: a payment changes the invoice's paid status and the amount left to pay"""

import allure
import pytest

pytestmark = [pytest.mark.api]


@allure.feature("Payments")
class TestPayments:
    def test_partial_payment(self, invoices_api, invoice, make_payment):
        response = make_payment(invoice, amount=3000)
        assert response.status_code == 200, response.text

        body = invoices_api.get(invoice["id"]).json()["data"]
        assert body["paid_status"] == "PARTIALLY_PAID"
        assert body["due_amount"] == 7000

    def test_full_payment(self, invoices_api, invoice, make_payment):
        response = make_payment(invoice, amount=10000)
        assert response.status_code == 200, response.text

        body = invoices_api.get(invoice["id"]).json()["data"]
        assert body["paid_status"] == "PAID"
        assert body["due_amount"] == 0
