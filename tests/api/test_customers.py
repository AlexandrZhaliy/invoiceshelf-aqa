import allure
import pytest

from framework.data.factories import customer_payload


pytestmark = pytest.mark.api

@allure.feature("Customers")
class TestCustomers:
    @allure.title("Created customer is returned with the same data and can be read back")
    def test_create_customer(self, customers_api):
        payload = customer_payload()

        created = customers_api.create(payload)
        assert created.status_code == 200
        data = created.json()["data"]
        assert data["name"] == payload["name"]
        assert data["email"] == payload["email"]
        assert data["phone"] == payload["phone"]

        try:
            fetched = customers_api.get(data["id"])
            assert fetched.status_code == 200
            assert fetched.json()["data"]["email"] == payload["email"]
        finally:
            customers_api.delete(data["id"])

    @allure.title("Second customer with an existing email is rejected")
    def test_duplicate_email_is_rejected(self, customers_api, customer):
        response = customers_api.create(customer_payload(email=customer["email"]))

        assert response.status_code == 422
        assert response.json()["errors"]["email"] == ["The email has already been taken."]

    @allure.title("Deleted customer is no longer available")
    def test_delete_customer(self, customers_api):
        created = customers_api.create(customer_payload()).json()["data"]

        deleted = customers_api.delete(created["id"])
        assert deleted.status_code == 200
        assert deleted.json() == {"success": True}

        assert customers_api.get(created["id"]).status_code == 404
