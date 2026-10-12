"""Users endpoint wrapper: one method per API call, returns the raw response, asserts nothing."""

import requests
from framework.api.client import ApiClient


class UsersApi:
    def __init__(self, client: ApiClient) -> None:
        self.client = client

    def create(self, payload: dict) -> requests.Response:
        return self.client.post("/api/v1/users", json=payload)

    def delete(self, user_id: int) -> requests.Response:
        # Bulk endpoint: POST /users/delete {"users": [...]} (the field is "users", not "ids" as in other areas)
        return self.client.post("/api/v1/users/delete", json={"users": [user_id]})
