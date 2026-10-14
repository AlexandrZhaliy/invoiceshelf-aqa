"""Catalog items (products the invoice form offers) endpoint wrapper: one method per API call, returns the raw response, asserts nothing."""

import requests
from framework.api.client import ApiClient


class CatalogItemsApi:
    def __init__(self, client: ApiClient) -> None:
        self.client = client

    def create(self, payload: dict) -> requests.Response:
        return self.client.post("/api/v1/items", json=payload)

    def delete(self, item_id: int) -> requests.Response:
        # Bulk endpoint: POST /items/delete {"ids": [...]}
        return self.client.post("/api/v1/items/delete", json={"ids": [item_id]})
