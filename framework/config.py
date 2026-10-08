"""Single source of test configuration.
Normally values come from .env file.
Defaults match docker-compose.yml, so `docker compose up` + `pytest` works with zero setup.CI overrides via env
"""

from __future__ import annotations
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv


load_dotenv()

def _env(name: str, default: str) -> str:
    return os.getenv(name, default)

@dataclass(frozen=True)
class Settings:
    base_url: str = field(default_factory=lambda: _env("BASE_URL", "http://localhost:8090").rstrip("/"))
    app_domain: str = field(default_factory=lambda: _env("APP_DOMAIN", "localhost:8090"))

    #============ Credentials the tests use after bootstrap ==================
    admin_email: str = field(default_factory=lambda: _env("ADMIN_EMAIL", "admin@example.com"))
    admin_password: str = field(default_factory=lambda: _env("ADMIN_PASSWORD", "1qaz2WSX3edc!"))
    company_name: str = field(default_factory=lambda: _env("COMPANY_NAME", "QA Portfolio TOV"))

    # ============ Localization: change these to relocalize the whole project ==================
    # Used by bootstrap (company country, currency, time zone) and by test data (phone numbers)
    country_code: str = field(default_factory=lambda: _env("COUNTRY_CODE", "UA"))  # ISO 3166-1 alpha-2
    currency_code: str = field(default_factory=lambda: _env("CURRENCY_CODE", "UAH"))  # ISO 4217
    time_zone: str = field(default_factory=lambda: _env("TIME_ZONE", "Europe/Kyiv"))  # IANA time zone
    phone_country_code: str = field(default_factory=lambda: _env("PHONE_COUNTRY_CODE", "+380"))

    # ================== Credentials created by the app's own seeder (used only once, by bootstrap)  ==================
    seed_admin_email: str = "admin@invoiceshelf.com"
    seed_admin_password: str = "invoiceshelf@123"

    # =========== Database: host/port as seen from the test runner, internal host as seen from the app container ======
    db_host: str = field(default_factory=lambda: _env("DB_HOST", "127.0.0.1"))
    db_port: int = field(default_factory=lambda: int(_env("DB_PORT", "3307")))
    db_internal_host: str = field(default_factory=lambda: _env("DB_INTERNAL_HOST", "database"))
    db_name: str = field(default_factory=lambda: _env("DB_NAME", "invoiceshelf"))
    db_user: str = field(default_factory=lambda: _env("DB_USER", "invoiceshelf"))
    db_password: str = field(default_factory=lambda: _env("DB_PASSWORD", "invoiceshelf"))

    request_timeout: float = field(default_factory=lambda: float(_env("REQUEST_TIMEOUT", "15")))

settings = Settings()