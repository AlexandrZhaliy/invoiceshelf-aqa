import allure
import pytest
from playwright.sync_api import Page, expect
from framework.config import settings
from framework.ui.login_page import LoginPage

pytestmark = [pytest.mark.ui]


@allure.feature("Login")
def test_admin_can_log_in(page: Page):
    login = LoginPage(page)
    login.open()
    login.log_in(settings.admin_email, settings.admin_password)

    expect(page).to_have_url(f"{settings.base_url}/admin/dashboard")

