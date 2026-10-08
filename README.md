# InvoiceShelf test automation

[![Tests](https://github.com/AlexandrZhaliy/invoiceshelf-aqa/actions/workflows/tests.yml/badge.svg)](https://github.com/AlexandrZhaliy/invoiceshelf-aqa/actions/workflows/tests.yml)
[![Allure report](https://img.shields.io/badge/Allure-latest%20report-blueviolet)](https://alexandrzhaliy.github.io/invoiceshelf-aqa/)

API and UI test automation framework for [InvoiceShelf](https://github.com/InvoiceShelf/InvoiceShelf), an open-source invoicing application. 
Stack: Python, pytest, Playwright, Docker Compose, GitHub Actions, Allure.

The goal of the project is not a high test count, but a framework that is easy to read, easy to extend and runs the same way on a laptop and in CI.

> **Status: work in progress.** Sections marked _Planned_ are not implemented yet.

## Allure report

_Screenshot: Planned._ The latest report from `main` is published at https://alexandrzhaliy.github.io/invoiceshelf-aqa/.

## System under test

InvoiceShelf `2.4.6`, the official Docker image, with MariaDB 10.11. The version is pinned on purpose: the upstream `latest` tag moves, and tests must not break because someone else published a release.

This repository contains only tests. It does not copy any InvoiceShelf code and is not affiliated with the InvoiceShelf project. InvoiceShelf is licensed under AGPL-3.0; it is used here as an unmodified Docker image.

## Quick start

Requirements: Docker with Compose, Python 3.13.

```bash
# 1. Start the application and its database, wait until both are healthy
docker compose up -d --wait

# 2. Install dependencies and complete the install wizard through the API
pip install -r requirements.txt
python scripts/bootstrap_app.py

# 3. Run the tests
pytest
```

The application is available at http://localhost:8090 (login `admin@example.com`, password `1qaz2WSX3edc!`). These are throwaway credentials of a local test environment. Defaults match `docker-compose.yml`; override them through environment variables or a `.env` file (see `.env.example`).

To look at the report locally (needs Java): `allure serve allure-results`.

To start from a clean state: `docker compose down -v`.

## Localization

The test environment is set up for Ukraine: company country `UA`, currency `UAH`, time zone `Europe/Kyiv`, phone numbers `+380`. Each value is a variable with a default in `framework/config.py`, so the whole project is relocalized in one place, through the environment or a `.env` file:

```bash
COUNTRY_CODE=PT CURRENCY_CODE=EUR TIME_ZONE=Europe/Lisbon PHONE_COUNTRY_CODE=+351
```

The company currency cannot be changed once transactions exist, so after changing these values start from a clean state (`docker compose down -v`). The application language stays English.

## Project layout

```
docker-compose.yml        System under test: InvoiceShelf + MariaDB, with healthchecks
scripts/bootstrap_app.py  Completes the install wizard through its API (idempotent)
framework/
  config.py               Single source of configuration (env variables, defaults for local run)
  api/client.py           HTTP client: base URL, auth header, timeouts, Allure attachments
  api/customers.py        One wrapper per API area: a method per call, returns the raw response
  data/factories.py       Test data builders, every call returns unique data
tests/
  conftest.py             Fixtures: readiness check, admin token, API clients, test entities
  api/                    API tests
.github/workflows/        CI: start the app, bootstrap, run tests, publish the Allure report
```

## Test strategy

| Layer | What it checks | Status |
|---|---|---|
| Smoke | The application is alive and an admin can log in | Done |
| API: auth | Wrong credentials, access without a token | Done |
| API: customers | Create and read back, duplicate email, delete | Done |
| API: invoices | Totals, validation errors, status transitions | _Planned_ |
| API: payments | Full and partial payment | _Planned_ |
| API: access control | Restricted role gets 403 | _Planned_ |
| DB | Stored data matches what the API reports | _Planned_ |
| UI (Playwright) | Login, create a customer, create an invoice through the form, record a payment | _Planned_ |
| E2E | Data prepared through the API, action in the UI, result verified through the API | _Planned_ |

Principles:

- **API for setup, UI for what only the UI can do.** Test data is created through the API, so UI tests stay short and fast.
- **Every test creates its own data** with unique values and does not depend on other tests or on execution order.
- **Tests clean up after themselves**, including when they fail (fixtures with `yield`).
- **Failure messages must explain the failure.** The readiness check stops the run with a clear message instead of producing dozens of unrelated red tests.

## Design decisions

- **The API client asserts nothing.** It sends requests, logs them to Allure and returns the response. Assertions live in tests, so every test reads as the check it makes. Wrappers per API area (`CustomersApi`) hold paths and payload shapes, so a change in the API is fixed in one place.
- **Fixture scopes.** The admin token is created once per run (`session`): logging in before every test is slow and adds nothing. Clients and test entities are created per test (`function`), because a test may change them.
- **The install wizard is automated through its API**, not through the UI: it is faster and does not depend on markup. See `scripts/bootstrap_app.py` for the details that are not obvious (the image runs migrations on start, so the wizard needs `database_overwrite`; the final steps are order-sensitive).
- **Secrets are never hard-coded in tests.** Configuration comes from the environment; passwords are masked in Allure attachments.

## CI

GitHub Actions (`.github/workflows/tests.yml`) on every push to `main` and on pull requests:

1. Start InvoiceShelf and MariaDB with `docker compose up --wait`
2. Complete the install wizard
3. Run the tests
4. Generate the Allure report and upload it as an artifact (also when tests fail)
5. On failure, upload container logs
6. On `main`, publish the report to GitHub Pages

## Observations about the application

Notes made while building the framework.

- For a non-existent resource the API answers `404` but the response body contains a full stack trace with server file paths. This happens because the test environment runs with `APP_DEBUG=true`; with debug off, such a response should not be returned. Worth keeping in mind when checking a production configuration.
- The install wizard refuses a fresh container with `database_should_be_empty`, because the Docker image runs migrations on start.

## How AI was used

_Planned: to be written at the end of the project, from what actually happened._

## License

[MIT](LICENSE)
