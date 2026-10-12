"""Invoice API tests. Money is in minor units: 5000 means 50.00."""

import allure
import pytest
from framework.data.factories import invoice_payload

pytestmark = [pytest.mark.api]


@allure.feature("Invoices")
class TestInvoices:
    def test_totals_are_calculated_from_items(self, invoices_api, invoice):
        """The invoice fixture has 1 x 5000 + 2 x 2500 lines."""
        body = invoices_api.get(invoice["id"]).json()["data"]

        assert body["sub_total"] == 10000
        assert body["total"] == 10000
        assert body["due_amount"] == 10000
        assert [i["total"] for i in body["items"]] == [5000, 5000]
        assert body["status"] == "DRAFT"
        assert body["paid_status"] == "UNPAID"

    def test_server_ignores_total_sent_by_client(self, invoices_api, customer):
        payload = invoice_payload(customer["id"], total=1)  # the lines say 10000
        response = invoices_api.create(payload)
        assert response.status_code == 200

        created = response.json()["data"]
        try:
            assert created["total"] == 10000
        finally:
            invoices_api.delete(created["id"])

    @pytest.mark.parametrize(
        "overrides",
        [
            pytest.param({"items": []}, id="no-items"),
            pytest.param({"customer_id": None}, id="no-customer"),
        ],
    )
    def test_invalid_payload_is_rejected(self, invoices_api, customer, overrides):
        payload = {**invoice_payload(customer["id"]), **overrides}
        response = invoices_api.create(payload)
        assert response.status_code == 422, response.text

    def test_duplicate_invoice_number_is_rejected(self, invoices_api, customer, invoice):
        payload = invoice_payload(customer["id"], invoice_number=invoice["invoice_number"])
        response = invoices_api.create(payload)
        assert response.status_code == 422, response.text

    def test_mark_as_sent(self, invoices_api, invoice):
        response = invoices_api.mark_as_sent(invoice["id"])
        assert response.status_code == 200, response.text
        assert invoices_api.get(invoice["id"]).json()["data"]["status"] == "SENT"