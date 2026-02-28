.PHONY: test test-cov test-unit test-integration install-test clean-test

# Install test dependencies
install-test:
	poetry install --with dev

# Run all tests
test:
	poetry run pytest -v

# Run tests with coverage
test-cov:
	poetry run pytest --cov=tera --cov-report=html --cov-report=term-missing

# Run specific module tests
test-users:
	poetry run pytest tests/test_users.py -v

test-company:
	poetry run pytest tests/test_company.py -v

test-employees:
	poetry run pytest tests/test_employees.py -v

test-payroll:
	poetry run pytest tests/test_payroll.py -v

test-finance:
	poetry run pytest tests/test_finance.py -v

# Run tests with specific markers (if you add markers later)
test-unit:
	poetry run pytest -m unit -v

test-integration:
	poetry run pytest -m integration -v

# Run tests and generate HTML coverage report
test-html:
	poetry run pytest --cov=tera --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

# Run tests with print statements visible
test-debug:
	poetry run pytest -v -s

# Clean test artifacts
clean-test:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -f .coverage
	rm -f coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Watch tests (requires pytest-watch)
test-watch:
	poetry run ptw

# Create test database
test-db-create:
	docker compose exec db psql -U postgres -c "DROP DATABASE IF EXISTS tera_test;"
	docker compose exec db psql -U postgres -c "CREATE DATABASE tera_test;"

# Run tests in Docker
test-docker:
	docker compose exec backend poetry run pytest -v

# Run specific test by name pattern
test-match:
	@read -p "Enter test name pattern: " pattern; \
	poetry run pytest -k "$$pattern" -v

# Show test collection without running
test-collect:
	poetry run pytest --collect-only

# Run failed tests from last run
test-failed:
	poetry run pytest --lf -v

# Help
help:
	@echo "Available test commands:"
	@echo "  make install-test    - Install test dependencies"
	@echo "  make test           - Run all tests"
	@echo "  make test-cov       - Run tests with coverage"
	@echo "  make test-users     - Run user module tests"
	@echo "  make test-company   - Run company module tests"
	@echo "  make test-employees - Run employee module tests"
	@echo "  make test-payroll   - Run payroll module tests"
	@echo "  make test-finance   - Run finance module tests"
	@echo "  make test-html      - Generate HTML coverage report"
	@echo "  make test-debug     - Run tests with print output"
	@echo "  make test-docker    - Run tests in Docker container"
	@echo "  make test-match     - Run tests matching pattern"
	@echo "  make test-collect   - Show test collection"
	@echo "  make test-failed    - Rerun failed tests"
	@echo "  make clean-test     - Clean test artifacts"
	@echo "  make test-db-create - Create test database"
