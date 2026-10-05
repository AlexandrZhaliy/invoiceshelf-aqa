"""Single source of test configuration.
Values come from .env file; defaults match docker-compose.yml,
so `docker compose up` + `pytest` works with zero setup.CI overrides via env
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
    admin_email: str = field(default_factory=lambda: _env("ADMIN_EMAIL", "qa.admin@example.com"))
    admin_password: str = field(default_factory=lambda: _env("ADMIN_PASSWORD", "Passw0rd!qa"))
    company_name: str = field(default_factory=lambda: _env("COMPANY_NAME", "QA Portfolio Lda"))

    #================== Credentials created by the app's own seeder (used only once, by bootstrap)  ==================
    seed_admin_email: str = "admin@invoiceshelf.com"
    seed_admin_password: str = "invoiceshelf@123"

    #=========== Database: host/port as seen from the test runner, internal host as seen from the app container ======
    db_host: str = field(default_factory=lambda: _env("DB_HOST", "127.0.0.1"))
    db_port: int = field(default_factory=lambda: int(_env("DB_PORT", "3307")))
    db_internal_host: str = field(default_factory=lambda: _env("DB_INTERNAL_HOST", "database"))
    db_name: str = field(default_factory=lambda: _env("DB_NAME", "invoiceshelf"))
    db_user: str = field(default_factory=lambda: _env("DB_USER", "invoiceshelf"))
    db_password: str = field(default_factory=lambda: _env("DB_PASSWORD", "invoiceshelf"))

    request_timeout: float = field(default_factory=lambda: float(_env("REQUEST_TIMEOUT", "15")))

settings = Settings()