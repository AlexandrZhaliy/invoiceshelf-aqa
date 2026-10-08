"""Walk through the InvoiceShelf install wizard via its API, so a fresh container is test-ready

The UI wizard (8 steps) calls the same endpoints; doing it over HTTP is faster and stable.
Idempotent: on an already-installed app it detects that and exits 0

Usage:  python scripts/bootstrap_app.py
"""

from __future__ import annotations
import sys
import time
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from framework.config import settings  # noqa: E402


INSTALL = f"{settings.base_url}/api/v1/installation"
TIMEOUT = 120  # migrate --seed runs inside the database/config call and can be slow

def log(msg: str) -> None:
    print(f"[bootstrap] {msg}", flush=True)

def wait_for_app(timeout_s: int = 180) -> None:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            if requests.get(f"{settings.base_url}/api/ping", timeout=5).status_code == 200:
                return
        except requests.ConnectionError:
            pass
        time.sleep(2)
    raise SystemExit(f"App did not answer /api/ping within {timeout_s}s")

def is_installed(session: requests.Session) -> bool:
    # Installation routes sit behind "redirect-if-installed": a finished install answers 302 -> /login
    resp = session.get(f"{INSTALL}/wizard-step", allow_redirects=False, timeout=10)
    if resp.status_code in (301, 302):
        return True
    resp.raise_for_status()
    return resp.json().get("profile_complete") == "COMPLETED"

def check(resp: requests.Response, step: str) -> dict:
    if not resp.ok:
        raise SystemExit(f"Step '{step}' failed: {resp.status_code} {resp.text[:500]}")
    body = resp.json() if resp.content else {}
    if isinstance(body, dict) and ("error" in body or "error_message" in body):
        raise SystemExit(f"Step '{step}' failed: {body}")
    log(f"ok: {step}")
    return body

def run() -> None:
    s = requests.Session()
    s.headers.update({"Accept": "application/json"})

    wait_for_app()
    if is_installed(s):
        log("already installed, nothing to do")
        return

    # Step 0: language
    check(s.post(f"{INSTALL}/wizard-language", json={"profile_language": "en"}, timeout=10), "language")

    # Step 3: database — this call writes .env and runs `migrate --seed` (creates admin + company)
    check(
        s.post(
            f"{INSTALL}/database/config",
            json={
                "app_url": settings.base_url,
                "app_locale": "en",
                "database_connection": "mariadb",
                "database_hostname": settings.db_internal_host,
                "database_port": 3306,
                "database_name": settings.db_name,
                "database_username": settings.db_user,
                "database_password": settings.db_password,
                # The Docker image auto-runs migrations on start (AUTORUN_ENABLED), so tables already exist
                # and the wizard refuses with "database_should_be_empty". Overwrite = wipe + migrate --seed
                # Safe here: we only get this far when is_installed() is False
                "database_overwrite": True,
            },
            timeout=TIMEOUT,
        ),
        "database + migrations",
    )

    # Step 4: domain (session/sanctum domains, matters for UI login)
    check(s.put(f"{INSTALL}/set-domain", json={"app_domain": settings.app_domain}, timeout=10), "domain")

    # Steps 6-8 need an authenticated user: the seeder created the super admin, log in with a token
    token = check(
        s.post(
            f"{settings.base_url}/api/v1/auth/login",
            json={
                "username": settings.seed_admin_email,
                "password": settings.seed_admin_password,
                "device_name": "bootstrap",
            },
            timeout=10,
        ),
        "login",
    )["token"]
    s.headers["Authorization"] = f"Bearer {token}"

    # Step 6: account
    check(
        s.put(
            f"{settings.base_url}/api/v1/me",
            json={
                "name": "QA Admin",
                "email": settings.admin_email,
                "password": settings.admin_password,
            },
            timeout=10,
        ),
        "account",
    )

    # Step 7: company. Country is looked up by ISO code: numeric ids are internal and may change
    countries = check(s.get(f"{settings.base_url}/api/v1/countries", timeout=10), "countries list")
    country_id = next(c["id"] for c in countries["data"] if c["code"] == settings.country_code)
    check(
        s.put(
            f"{settings.base_url}/api/v1/company",
            json={"name": settings.company_name, "address": {"country_id": country_id}},
            timeout=10,
        ),
        "company",
    )

    # Step 8: preferences. Currency is looked up by code instead of a hardcoded id
    currencies = check(s.get(f"{settings.base_url}/api/v1/currencies", timeout=10), "currencies list")
    currency_id = next(c["id"] for c in currencies["data"] if c["code"] == settings.currency_code)
    check(
        s.post(
            f"{settings.base_url}/api/v1/company/settings",
            json={
                "settings": {
                    "currency": currency_id,
                    "language": "en",
                    "carbon_date_format": "Y-m-d",
                    "time_zone": settings.time_zone,
                    "fiscal_year": "1-12",
                }
            },
            timeout=10,
        ),
        "preferences",
    )

    # Order matters: once profile_complete=COMPLETED, every /installation/* route redirects to /login
    check(s.post(f"{INSTALL}/finish", timeout=10), "finish")
    check(s.post(f"{INSTALL}/wizard-step", json={"profile_complete": "COMPLETED"}, timeout=10), "mark completed")

    if not is_installed(requests.Session()):
        raise SystemExit("Wizard finished but the app does not report itself as installed")
    log(f"done: login with {settings.admin_email}")


if __name__ == "__main__":
    run()


