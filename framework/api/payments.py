"""Payments endpoint wrapper: one method per API call, returns the raw response, asserts nothing."""

import requests
from framework.api.client import ApiClient


class PaymentsApi:
    def __init__(self, client: ApiClient) -> None:
        self.client = client

    def create(self, payload: dict) -> requests.Response:
        return self.client.post("/api/v1/payments", json=payload)

    def delete(self, payment_id: int) -> requests.Response:
        # Used only for test cleanup. Hard delete is a product feature, see Observations in README
        # Bulk endpoint: POST /payments/delete {"ids": [...]}
        return self.client.post("/api/v1/payments/delete", json={"ids": [payment_id]})
