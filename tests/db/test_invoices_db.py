"""The data the API reports must be what is actually stored."""

import allure
import pytest

pytestmark = [pytest.mark.db]


@allure.feature("Invoices")
def test_invoice_row_matches_api(db, invoices_api, invoice):
    api_data = invoices_api.get(invoice["id"]).json()["data"]

    row = db.fetch_one(
        "SELECT invoice_number, total, due_amount, status, paid_status FROM invoices WHERE id = %s",
        (invoice["id"],),
    )

    assert row is not None, "Invoice exists in the API but not in the database"
    assert row["invoice_number"] == api_data["invoice_number"]
    assert row["total"] == api_data["total"] == 10000
    assert row["due_amount"] == api_data["due_amount"]
    assert row["status"] == api_data["status"]
    assert row["paid_status"] == api_data["paid_status"]
