"""Just a smoke-test if the product starts at all"""

import allure
import pytest
from framework.config import settings

pytestmark = [pytest.mark.smoke, pytest.mark.api]

@allure.title("API is up: /api/ping answers")
def test_ping(api):
    response = api.get("/api/ping")

    assert response.status_code == 200
    assert response.json() == {"success": "invoiceshelf-self-hosted"}


@allure.title("Admin gets a token and sees own profile")
def test_admin_can_login_and_read_profile(api):
    login = api.login(settings.admin_email, settings.admin_password)
    assert login.status_code == 200
    assert login.json()["type"] == "Bearer"

    api.set_token(login.json()["token"])
    me = api.get("/api/v1/me")

    assert me.status_code == 200
    assert me.json()["data"]["email"] == settings.admin_email