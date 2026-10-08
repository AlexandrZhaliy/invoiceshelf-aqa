"""Test data builders.

Every call returns UNIQUE data (uuid suffix): tests must never collide with each other or with
leftovers from a previous run, and must not depend on execution order.
"""

from __future__ import annotations
import uuid
import random

from framework.config import settings

# Deliberately invalid number (real numbers never start with 0 after the country code): can't match a real person.
# Caveat: a future phone-format validation may reject it.
FAKE_PHONE_PREFIX = f"{settings.phone_country_code}000"


def unique_suffix() -> str:
    return uuid.uuid4().hex[:8]


def customer_payload(**overrides) -> dict:
    suffix = unique_suffix()
    phone_suffix = f"{random.randint(0, 999999):06d}"
    payload = {
        "name": f"QA Customer {suffix}",
        "email": f"qa.customer.{suffix}@example.com",  # example.com is reserved for tests
        "phone": f"{FAKE_PHONE_PREFIX}{phone_suffix}",
    }
    payload.update(overrides)
    return payload
