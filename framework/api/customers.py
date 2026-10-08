"""Customers endpoint wrapper: one method per API call, returns the raw response, asserts nothing."""

from __future__ import annotations
import requests
from framework.api.client import ApiClient


class CustomersApi:
    def __init__(self, client: ApiClient) -> None:
        self.client = client

    def create(self, payload: dict) -> requests.Response:
        return self.client.post("/api/v1/customers", json=payload)

    def get(self, customer_id: int) -> requests.Response:
        return self.client.get(f"/api/v1/customers/{customer_id}")

    def list(self, **params) -> requests.Response:
        return self.client.get("/api/v1/customers", params=params)

    def delete(self, customer_id: int) -> requests.Response:
        # The API deletes in bulk: POST /customers/delete {"ids": [...]}
        return self.client.post("/api/v1/customers/delete", json={"ids": [customer_id]})