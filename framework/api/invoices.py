"""Invoices endpoint wrapper: one method per API call, returns the raw response, asserts nothing."""

import requests
from framework.api.client import ApiClient


class InvoicesApi:
    def __init__(self, client: ApiClient) -> None:
        self.client = client

    def create(self, payload: dict) -> requests.Response:
        return self.client.post("/api/v1/invoices", json=payload)

    def list(self) -> requests.Response:
        return self.client.get("/api/v1/invoices")

    # invoice-ids are sequential integers (auto-increment). Access checks by id are covered within test_access.py
    def get(self, invoice_id: int) -> requests.Response:
        return self.client.get(f"/api/v1/invoices/{invoice_id}")

    def mark_as_sent(self, invoice_id: int) -> requests.Response:
        return self.client.post(f"/api/v1/invoices/{invoice_id}/status", json={"status": "SENT"})

    def delete(self, invoice_id: int) -> requests.Response:
        # Bulk endpoint: POST /invoices/delete {"ids": [...]}
        return self.client.post("/api/v1/invoices/delete", json={"ids": [invoice_id]})
