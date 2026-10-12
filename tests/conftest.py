"""Shared fixtures.

Scope rule of thumb:
- session: expensive and read-only (app readiness, admin token)
- function: anything a test can change (clients, created entities)
"""

import pytest
import requests
from framework.api import ApiClient
from framework.api.customers import CustomersApi
from framework.api.invoices import InvoicesApi
from framework.api.payments import PaymentsApi
from framework.api.reference import ReferenceApi
from framework.api.roles import RolesApi
from framework.api.users import UsersApi
from framework.config import settings
from framework.db import Database
from framework.data.factories import (
    customer_payload,
    invoice_payload,
    payment_payload,
    role_payload,
    user_payload,
)


@pytest.fixture(scope="session", autouse=True)
def app_ready() -> None:
    """Fail fast with a clear message instead of 50 red tests if the app is down or not installed."""
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
    """Anonymous client — for auth and access-control tests."""
    return ApiClient()


@pytest.fixture(scope="session")
def admin_token() -> str:
    """One login per run: tokens are cheap to reuse, and logging in before every test is slow noise."""
    response = ApiClient().login(settings.admin_email, settings.admin_password)
    assert response.status_code == 200, f"Admin login failed: {response.status_code} {response.text}"
    return response.json()["token"]


@pytest.fixture
def admin_api(admin_token: str) -> ApiClient:
    """Client authenticated as the company owner (super admin)."""
    return ApiClient(token=admin_token)


@pytest.fixture(scope="session")
def company_currency_id(admin_token: str) -> int:
    return ReferenceApi(ApiClient(token=admin_token)).company_currency_id()


@pytest.fixture(scope="session")
def payment_method_id(admin_token: str) -> int:
    return ReferenceApi(ApiClient(token=admin_token)).payment_method_id("Cash")


@pytest.fixture(scope="session")
def db():
    database = Database()
    yield database
    database.close()


@pytest.fixture
def customers_api(admin_api: ApiClient) -> CustomersApi:
    return CustomersApi(admin_api)


@pytest.fixture
def invoices_api(admin_api: ApiClient) -> InvoicesApi:
    return InvoicesApi(admin_api)

@pytest.fixture
def payments_api(admin_api: ApiClient) -> PaymentsApi:
    return PaymentsApi(admin_api)

@pytest.fixture
def customer(customers_api: CustomersApi, company_currency_id: int):
    """A fresh customer for tests that need one but are not testing creation. Deleted afterwards.

    Created in the company currency: otherwise the API demands an exchange rate for every invoice.
    """
    response = customers_api.create(customer_payload(currency_id=company_currency_id))
    assert response.status_code == 200, f"Fixture could not create customer: {response.text}"
    created = response.json()["data"]

    yield created

    customers_api.delete(created["id"])


@pytest.fixture
def invoice(invoices_api: InvoicesApi, customer: dict):
    """A draft invoice with two lines (1 x 50.00 + 2 x 25.00 = 100.00, i.e. 10000 minor units)"""
    response = invoices_api.create(invoice_payload(customer["id"]))
    assert response.status_code == 200, f"Fixture could not create invoice: {response.text}"
    created = response.json()["data"]

    yield created

    invoices_api.delete(created["id"])

@pytest.fixture
def make_payment(payments_api: PaymentsApi, customer: dict, payment_method_id: int):
    """Factory: records a payment against an invoice and removes every payment it made afterwards."""
    created_ids: list[int] = []

    def _make(invoice: dict, amount: int):
        response = payments_api.create(payment_payload(customer["id"], invoice["id"], amount, payment_method_id))
        if response.status_code == 200:
            created_ids.append(response.json()["data"]["id"])
        return response

    yield _make

    for payment_id in created_ids:
        payments_api.delete(payment_id)

@pytest.fixture
def limited_api(admin_api: ApiClient) -> ApiClient:
    """Client logged in as a user whose role only allows viewing items. User and role are removed afterwards."""
    users, roles = UsersApi(admin_api), RolesApi(admin_api)

    role = roles.create(role_payload())
    assert role.status_code == 201, f"Fixture could not create role: {role.text}"
    role_data = role.json()["data"]

    company_id = ReferenceApi(admin_api).company_id()
    payload = user_payload(role_data["name"], company_id)
    user = users.create(payload)
    assert user.status_code == 201, f"Fixture could not create user: {user.text}"
    user_id = user.json()["data"]["id"]

    login = ApiClient().login(payload["email"], payload["password"])
    assert login.status_code == 200, f"Limited user could not log in: {login.text}"

    yield ApiClient(token=login.json()["token"])

    # The user first: the app refuses to delete a role that is still assigned to a user.
    # Cleanup results are checked: a silently failing delete would leave users and roles behind.
    assert users.delete(user_id).status_code == 200
    assert roles.delete(role_data["id"]).status_code == 200