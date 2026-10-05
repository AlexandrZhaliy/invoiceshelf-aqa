from __future__ import annotations
import pytest
import requests
from framework.api import ApiClient
from framework.config import settings


@pytest.fixture(scope="session", autouse=True)
def app_ready() -> None:
    """Fail fast with a clear message instead of 50 red tests if the app is down or not installed"""
    try:
        requests.get(f"{settings.base_url}/api/ping", timeout=5).raise_for_status()
    except requests.RequestException as exc:
        pytest.exit(f"App is not reachable at {settings.base_url}: {exc}. Run `docker compose up -d --wait`.", 2)

    wizard = requests.get(
        f"{settings.base_url}/api/v1/installation/wizard-step", allow_redirects=False, timeout=5
    )
    if wizard.status_code not in (301, 302):
        pytest.exit("App is not installed yet. Run `python scripts/bootstrap_app.py`.", 2)


@pytest.fixture
def api() -> ApiClient:
    """Anonymous client — for auth and access-control tests"""
    return ApiClient()


@pytest.fixture(scope="session")
def admin_token() -> str:
    """One login per run: tokens are cheap to reuse, and logging in before every test is slow noise"""
    response = ApiClient().login(settings.admin_email, settings.admin_password)
    assert response.status_code == 200, f"Admin login failed: {response.status_code} {response.text}"
    return response.json()["token"]


@pytest.fixture
def admin_api(admin_token: str) -> ApiClient:
    """Client authenticated as the company owner (super-admin)"""
    return ApiClient(token=admin_token)
