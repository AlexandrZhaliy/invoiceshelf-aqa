"""Test data builders.
Every call returns UNIQUE data (uuid suffix): tests must never collide with each other or with
leftovers from a previous run, and must not depend on execution order.
"""

import uuid
import random
from datetime import date, timedelta

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

def item_payload(name: str | None = None, quantity: int = 1, price: int = 1000, **overrides) -> dict:
    # One invoice line. Money is in minor units (kopiykas): price=5000 means 50.00
    # Note: the API fails with 500 if a line has no discount, discount_val, discount_type, tax
    item = {
        "name": name or f"QA Item {unique_suffix()}",
        "description": "",
        "quantity": quantity,
        "price": price,
        "discount": 0,
        "discount_val": 0,
        "discount_type": "fixed",
        "tax": 0,
    }
    item.update(overrides)
    return item

def invoice_payload(customer_id: int, items: list[dict] | None = None, **overrides) -> dict:
    items = items if items is not None else [item_payload(quantity=1, price=5000), item_payload(quantity=2, price=2500)]
    sub_total = sum(i["quantity"] * i["price"] for i in items)
    today = date.today()
    payload = {
        "invoice_number": f"QA-INVOICE-{unique_suffix()}",
        "invoice_date": today.isoformat(),
        "due_date": (today + timedelta(days=3)).isoformat(),
        "customer_id": customer_id,
        "template_name": "invoice1",
        "items": items,
        "sub_total": sub_total,
        "total": sub_total,
        "discount": 0,
        "discount_val": 0,
        "discount_type": "fixed",
        "tax": 0,
    }
    payload.update(overrides)
    return payload

def payment_payload(customer_id: int, invoice_id: int, amount: int, payment_method_id: int, **overrides) -> dict:
    payload = {
        "payment_number": f"QA-PAYMENT-{unique_suffix()}",
        "payment_date": date.today().isoformat(),
        "customer_id": customer_id,
        "invoice_id": invoice_id,
        "payment_method_id": payment_method_id,
        "amount": amount,
        "notes": "",
    }
    payload.update(overrides)
    return payload

def role_payload(**overrides) -> dict:
    """A role that can only view items and cannot view invoices and payments"""
    payload = {"name": f"qa-items-only-{unique_suffix()}", "abilities": [{"ability": "view-item"}]}
    payload.update(overrides)
    return payload

def user_payload(role_name: str, company_id: int, **overrides) -> dict:
    suffix = unique_suffix()
    payload = {
        "name": f"QA Limited User {suffix}",
        "email": f"qa.limited.{suffix}@example.com",
        "password": f"Qa-{unique_suffix()}-1!",  # random per user: no shared password to hard-code
        "companies": [{"id": company_id, "role": role_name}],
    }
    payload.update(overrides)
    return payload