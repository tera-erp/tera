"""Tests for the company module."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tera.modules.users.models import User
from tera.modules.company.models import Company, CompanyStatus


class TestCompanyCRUD:
    """Test company CRUD operations."""

    async def test_create_company_as_admin(self, client: AsyncClient,
                                           auth_headers: dict):
        """Test creating a company as admin."""
        company_data = {
            "name": "New Company",
            "legal_name": "New Company Ltd",
            "country_code": "USA",
            "currency_code": "USD",
            "timezone": "America/New_York",
            "status": "ACTIVE"
        }
        response = await client.post("/api/v1/companies/",
                                     json=company_data,
                                     headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == company_data["name"]
        assert data["country_code"] == company_data["country_code"]

    async def test_create_company_duplicate_name(self, client: AsyncClient,
                                                 test_company: Company,
                                                 auth_headers: dict):
        """Test creating company with duplicate name."""
        company_data = {
            "name": test_company.name,
            "legal_name": "Another Legal Name",
            "country_code": "USA",
            "currency_code": "USD",
            "timezone": "UTC"
        }
        response = await client.post("/api/v1/companies/",
                                     json=company_data,
                                     headers=auth_headers)
        assert response.status_code == 400

    async def test_list_companies(self, client: AsyncClient,
                                  test_company: Company, auth_headers: dict):
        """Test listing companies."""
        response = await client.get("/api/v1/companies/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(c["name"] == test_company.name for c in data)

    async def test_get_company_by_id(self, client: AsyncClient,
                                     test_company: Company,
                                     auth_headers: dict):
        """Test getting company by ID."""
        response = await client.get(f"/api/v1/companies/{test_company.id}",
                                    headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_company.id
        assert data["name"] == test_company.name

    async def test_get_current_company(self, client: AsyncClient,
                                       test_company: Company,
                                       test_admin_user: User,
                                       auth_headers: dict):
        """Test getting current user's company."""
        response = await client.get("/api/v1/companies/current",
                                    headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_company.id

    async def test_update_company(self, client: AsyncClient,
                                  test_company: Company, auth_headers: dict):
        """Test updating company."""
        update_data = {
            "legal_name": "Updated Legal Name",
            "timezone": "America/Los_Angeles"
        }
        response = await client.patch(f"/api/v1/companies/{test_company.id}",
                                      json=update_data,
                                      headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["legal_name"] == "Updated Legal Name"
        assert data["timezone"] == "America/Los_Angeles"

    async def test_delete_company(self, client: AsyncClient,
                                  db_session: AsyncSession,
                                  auth_headers: dict):
        """Test deleting company."""
        # Create a company to delete
        company = Company(name="Company To Delete",
                          legal_name="Company To Delete Ltd",
                          country_code="CAN",
                          currency_code="CAD",
                          timezone="UTC",
                          status=CompanyStatus.ACTIVE)
        db_session.add(company)
        await db_session.commit()
        await db_session.refresh(company)

        response = await client.delete(f"/api/v1/companies/{company.id}",
                                       headers=auth_headers)
        assert response.status_code == 204


class TestCompanyAuthorization:
    """Test company authorization."""

    async def test_employee_cannot_create_company(self, client: AsyncClient,
                                                  employee_auth_headers: dict):
        """Test that employees cannot create companies."""
        company_data = {
            "name": "Unauthorized Company",
            "legal_name": "Unauthorized Company Ltd",
            "country_code": "USA",
            "currency_code": "USD",
            "timezone": "UTC"
        }
        response = await client.post("/api/v1/companies/",
                                     json=company_data,
                                     headers=employee_auth_headers)
        assert response.status_code == 403

    async def test_employee_can_view_own_company(self, client: AsyncClient,
                                                 test_company: Company,
                                                 employee_auth_headers: dict):
        """Test that employees can view their own company."""
        response = await client.get("/api/v1/companies/current",
                                    headers=employee_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_company.id

    async def test_hr_admin_cannot_create_company(self, client: AsyncClient,
                                                  hr_auth_headers: dict):
        """Test that HR admins cannot create companies."""
        company_data = {
            "name": "HR Company",
            "legal_name": "HR Company Ltd",
            "country_code": "USA",
            "currency_code": "USD",
            "timezone": "UTC"
        }
        response = await client.post("/api/v1/companies/",
                                     json=company_data,
                                     headers=hr_auth_headers)
        assert response.status_code == 403


class TestCompanyValidation:
    """Test company data validation."""

    async def test_invalid_country_code(self, client: AsyncClient,
                                        auth_headers: dict):
        """Test creating company with invalid country code."""
        company_data = {
            "name": "Invalid Country Company",
            "legal_name": "Invalid Country Company Ltd",
            "country_code": "XY",  # Invalid 2-letter code instead of 3
            "currency_code": "USD",
            "timezone": "UTC"
        }
        response = await client.post("/api/v1/companies/",
                                     json=company_data,
                                     headers=auth_headers)
        assert response.status_code == 422

    async def test_invalid_currency_code(self, client: AsyncClient,
                                         auth_headers: dict):
        """Test creating company with invalid currency code."""
        company_data = {
            "name": "Invalid Currency Company",
            "legal_name": "Invalid Currency Company Ltd",
            "country_code": "USA",
            "currency_code": "INVALID",
            "timezone": "UTC"
        }
        response = await client.post("/api/v1/companies/",
                                     json=company_data,
                                     headers=auth_headers)
        assert response.status_code == 422


class TestCompanyReferences:
    """Test company reference data endpoints."""

    async def test_get_currencies(self, client: AsyncClient,
                                  auth_headers: dict):
        """Test getting list of supported currencies."""
        response = await client.get("/api/v1/companies/currencies",
                                    headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "USD" in data
        assert "EUR" in data

    async def test_get_countries(self, client: AsyncClient,
                                 auth_headers: dict):
        """Test getting list of supported countries."""
        response = await client.get("/api/v1/companies/countries",
                                    headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "USA" in data or "United States" in data
