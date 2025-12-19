# Running Tests

This directory contains comprehensive pytest tests for all backend modules.

## Setup

1. Install test dependencies:
```bash
poetry install --with dev
```

2. Set up a test database:
```bash
# Create test database
docker compose exec db psql -U postgres -c "CREATE DATABASE tera_test;"
```

3. Update test database URL in `tests/conftest.py` if needed:
```python
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/tera_test"
```

## Running Tests

### Run all tests
```bash
poetry run pytest
```

### Run specific test file
```bash
poetry run pytest tests/test_users.py
```

### Run specific test class
```bash
poetry run pytest tests/test_users.py::TestUserAuthentication
```

### Run specific test
```bash
poetry run pytest tests/test_users.py::TestUserAuthentication::test_login_success
```

### Run with coverage
```bash
poetry run pytest --cov=tera --cov-report=html
```

### Run with verbose output
```bash
poetry run pytest -v
```

### Run and show print statements
```bash
poetry run pytest -s
```

## Test Structure

- `conftest.py` - Shared fixtures and test configuration
- `test_users.py` - User authentication and management tests
- `test_company.py` - Company CRUD and validation tests
- `test_employees.py` - Employee profile and status tests
- `test_payroll.py` - Payroll run and payslip tests
- `test_finance.py` - Invoice and customer management tests

## Fixtures

Common fixtures available in all tests:

- `client` - Async HTTP client for API testing
- `db_session` - Fresh database session per test
- `test_company` - Test company instance
- `test_admin_user` - IT admin user
- `test_hr_admin_user` - HR admin user
- `test_employee_user` - Regular employee user
- `test_employee_profile` - Employee profile
- `auth_headers` - Authorization headers for admin
- `hr_auth_headers` - Authorization headers for HR admin
- `employee_auth_headers` - Authorization headers for employee
