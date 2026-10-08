import allure
import pytest

from framework.config import settings


pytestmark = pytest.mark.api

@allure.feature("Auth")
@allure.title("Login with a wrong password is rejected and gives no token")
def test_login_with_wrong_password_is_rejected(api):
    response = api.login(settings.admin_email, "definitely-wrong-password")

    assert response.status_code == 422
    body = response.json()
    assert "token" not in body
    assert body["errors"]["email"] == ["The provided credentials are incorrect."]

@allure.feature("Auth")
@allure.title("Protected endpoint without a token answers 401")
def test_protected_endpoint_requires_authentication(api):
    response = api.get("/api/v1/customers")

    assert response.status_code == 401
    assert response.json() == {"message": "Unauthenticated."}
