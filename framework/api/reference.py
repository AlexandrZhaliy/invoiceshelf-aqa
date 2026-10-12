"""Reference data every document depends on: company_id, its currency_ids and payment methods"""

from framework.api.client import ApiClient


class ReferenceApi:
    def __init__(self, client: ApiClient) -> None:
        self.client = client

    def company_currency_id(self) -> int:
        response = self.client.get("/api/v1/company/settings", params={"settings": ["currency"]})
        response.raise_for_status()
        return int(response.json()["currency"])

    def payment_method_id(self, name: str = "Cash") -> int:
        response = self.client.get("/api/v1/payment-methods")
        response.raise_for_status()
        return next(m["id"] for m in response.json()["data"] if m["name"] == name)

    def company_id(self) -> int:
        response = self.client.get("/api/v1/companies")
        response.raise_for_status()
        return response.json()["data"][0]["id"]
