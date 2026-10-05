"""Thin HTTP client for the InvoiceShelf REST API
It knows the base URL, auth header and timeouts, and logs every call to Allure
It does NOT assert anything — assertions live in tests, so a test reads as the check it makes
"""

from __future__ import annotations
import json
from typing import Any
import allure
import requests
from framework.config import settings


class ApiClient:
    def __init__(self, base_url: str = settings.base_url, token: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        if token:
            self.set_token(token)

    # ======================== auth ============================
    def set_token(self, token: str) -> None:
        self.session.headers["Authorization"] = f"Bearer {token}"

    def login(self, email: str, password: str, device_name: str = "pytest") -> requests.Response:
        return self.post(
            "/api/v1/auth/login",
            json={"username": email, "password": password, "device_name": device_name},
        )

    # ======================== http verbs ============================
    def get(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("DELETE", path, **kwargs)

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        kwargs.setdefault("timeout", settings.request_timeout)
        url = f"{self.base_url}{path}"
        with allure.step(f"{method} {path}"):
            response = self.session.request(method, url, **kwargs)
            _attach(method, url, kwargs, response)
        return response


def _attach(method: str, url: str, kwargs: dict, response: requests.Response) -> None:
    request_body = kwargs.get("json") or kwargs.get("data") or kwargs.get("params")
    req = f"{method} {url}"
    if request_body is not None:
        req += "\n\n" + _pretty(request_body)
    allure.attach(_mask(req), name="request", attachment_type=allure.attachment_type.TEXT)
    allure.attach(
        f"{response.status_code} ({response.elapsed.total_seconds():.2f}s)\n\n{_pretty(response.text)}",
        name="response",
        attachment_type=allure.attachment_type.TEXT,
    )

def _pretty(body: Any) -> str:
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except ValueError:
            return body[:5000]
    return json.dumps(body, indent=2, ensure_ascii=False)[:5000]

def _mask(text: str) -> str:
    """Never leak passwords into reports."""
    for secret in (settings.admin_password, settings.seed_admin_password):
        text = text.replace(secret, "***")
    return text
