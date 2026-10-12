"""Roles endpoint wrapper: one method per API call, returns the raw response, asserts nothing."""

import requests
from framework.api.client import ApiClient


class RolesApi:
    def __init__(self, client: ApiClient) -> None:
        self.client = client

    def create(self, payload: dict) -> requests.Response:
        return self.client.post("/api/v1/roles", json=payload)

    def delete(self, role_id: int) -> requests.Response:
        return self.client.delete(f"/api/v1/roles/{role_id}")
