"""Tests for the users module."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tera.modules.users.models import User, UserRole, UserStatus
from tera.modules.company.models import Company


class TestUserSetup:
    """Test user setup endpoints."""
    
    async def test_setup_status_no_admin(self, client: AsyncClient):
        """Test setup status when no admin exists."""
        response = await client.get("/api/v1/users/setup/status")
        assert response.status_code == 200
        data = response.json()
        assert data["is_initialized"] == False
        assert data["admin_exists"] == False
    
    async def test_setup_status_with_admin(
        self,
        client: AsyncClient,
        test_admin_user: User
    ):
        """Test setup status when admin exists."""
        response = await client.get("/api/v1/users/setup/status")
        assert response.status_code == 200
        data = response.json()
        assert data["is_initialized"] == True
        assert data["admin_exists"] == True
    
    async def test_setup_admin_success(self, client: AsyncClient):
        """Test creating admin account."""
        admin_data = {
            "email": "admin@newcompany.com",
            "username": "newadmin",
            "first_name": "New",
            "last_name": "Admin",
            "password": "securepass123",
            "company_name": "New Company",
            "country_code": "USA"
        }
        response = await client.post("/api/v1/users/setup/admin", json=admin_data)
        assert response.status_code == 201
        data = response.json()
        assert data["access_token"]
        assert data["user"]["email"] == admin_data["email"]
        assert data["user"]["role"] == "IT_ADMIN"
    
    async def test_setup_admin_already_exists(
        self,
        client: AsyncClient,
        test_admin_user: User
    ):
        """Test that setup fails when admin already exists."""
        admin_data = {
            "email": "another@admin.com",
            "username": "anotheradmin",
            "first_name": "Another",
            "last_name": "Admin",
            "password": "securepass123",
            "company_name": "Another Company",
            "country_code": "USA"
        }
        response = await client.post("/api/v1/users/setup/admin", json=admin_data)
        assert response.status_code == 400


class TestUserAuthentication:
    """Test user authentication endpoints."""
    
    async def test_login_success(
        self,
        client: AsyncClient,
        test_admin_user: User
    ):
        """Test successful login."""
        login_data = {
            "username": "admin",
            "password": "testpass123"
        }
        response = await client.post("/api/v1/users/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"]
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "admin"
    
    async def test_login_wrong_password(
        self,
        client: AsyncClient,
        test_admin_user: User
    ):
        """Test login with wrong password."""
        login_data = {
            "username": "admin",
            "password": "wrongpassword"
        }
        response = await client.post("/api/v1/users/login", json=login_data)
        assert response.status_code == 401
    
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with nonexistent user."""
        login_data = {
            "username": "nonexistent",
            "password": "somepassword"
        }
        response = await client.post("/api/v1/users/login", json=login_data)
        assert response.status_code == 401
    
    async def test_get_current_user(
        self,
        client: AsyncClient,
        test_admin_user: User,
        auth_headers: dict
    ):
        """Test getting current user info."""
        response = await client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["email"] == "admin@test.com"
    
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test getting current user without token."""
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 401


class TestUserCRUD:
    """Test user CRUD operations."""
    
    async def test_create_user_as_admin(
        self,
        client: AsyncClient,
        test_company: Company,
        auth_headers: dict
    ):
        """Test creating a user as admin."""
        user_data = {
            "email": "newuser@test.com",
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "password": "password123",
            "phone": "+1234567890",
            "role": "EMPLOYEE",
            "status": "ACTIVE",
            "company_id": test_company.id
        }
        response = await client.post(
            f"/api/v1/users/companies/{test_company.id}",
            json=user_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "hashed_password" not in data
    
    async def test_create_user_duplicate_email(
        self,
        client: AsyncClient,
        test_company: Company,
        test_employee_user: User,
        auth_headers: dict
    ):
        """Test creating user with duplicate email."""
        user_data = {
            "email": test_employee_user.email,
            "username": "different",
            "first_name": "New",
            "last_name": "User",
            "password": "password123",
            "company_id": test_company.id
        }
        response = await client.post(
            f"/api/v1/users/companies/{test_company.id}",
            json=user_data,
            headers=auth_headers
        )
        assert response.status_code == 400
    
    async def test_list_users(
        self,
        client: AsyncClient,
        test_company: Company,
        test_admin_user: User,
        test_employee_user: User,
        auth_headers: dict
    ):
        """Test listing users."""
        response = await client.get(
            f"/api/v1/users/companies/{test_company.id}/",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        usernames = [u["username"] for u in data]
        assert "admin" in usernames
        assert "employee" in usernames
    
    async def test_get_user_by_id(
        self,
        client: AsyncClient,
        test_employee_user: User,
        auth_headers: dict
    ):
        """Test getting user by ID."""
        response = await client.get(
            f"/api/v1/users/{test_employee_user.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_employee_user.id
        assert data["username"] == test_employee_user.username
    
    async def test_update_user(
        self,
        client: AsyncClient,
        test_employee_user: User,
        auth_headers: dict
    ):
        """Test updating user."""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone": "+9876543210"
        }
        response = await client.patch(
            f"/api/v1/users/{test_employee_user.id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["phone"] == "+9876543210"
    
    async def test_delete_user(
        self,
        client: AsyncClient,
        test_employee_user: User,
        auth_headers: dict
    ):
        """Test deleting user."""
        response = await client.delete(
            f"/api/v1/users/{test_employee_user.id}",
            headers=auth_headers
        )
        assert response.status_code == 204
        
        # Verify user is deleted
        response = await client.get(
            f"/api/v1/users/{test_employee_user.id}",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestUserAuthorization:
    """Test user authorization and permissions."""
    
    async def test_employee_cannot_create_user(
        self,
        client: AsyncClient,
        test_company: Company,
        employee_auth_headers: dict
    ):
        """Test that regular employees cannot create users."""
        user_data = {
            "email": "newuser@test.com",
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "password": "password123",
            "company_id": test_company.id
        }
        response = await client.post(
            f"/api/v1/users/companies/{test_company.id}",
            json=user_data,
            headers=employee_auth_headers
        )
        assert response.status_code == 403
    
    async def test_hr_admin_can_create_user(
        self,
        client: AsyncClient,
        test_company: Company,
        hr_auth_headers: dict
    ):
        """Test that HR admins can create users."""
        user_data = {
            "email": "hruser@test.com",
            "username": "hruser",
            "first_name": "HR",
            "last_name": "User",
            "password": "password123",
            "company_id": test_company.id
        }
        response = await client.post(
            f"/api/v1/users/companies/{test_company.id}",
            json=user_data,
            headers=hr_auth_headers
        )
        assert response.status_code == 201
    
    async def test_employee_can_view_own_profile(
        self,
        client: AsyncClient,
        test_employee_user: User,
        employee_auth_headers: dict
    ):
        """Test that employees can view their own profile."""
        response = await client.get(
            "/api/v1/users/me",
            headers=employee_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_employee_user.username
