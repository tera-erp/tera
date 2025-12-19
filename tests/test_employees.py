"""Tests for the employees module."""
import pytest
from datetime import date
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tera.modules.users.models import User
from tera.modules.company.models import Company
from tera.modules.employees.models import EmployeeProfile, EmployeeStatus


class TestEmployeeCRUD:
    """Test employee CRUD operations."""
    
    async def test_create_employee(
        self,
        client: AsyncClient,
        test_company: Company,
        test_employee_user: User,
        auth_headers: dict
    ):
        """Test creating an employee profile."""
        employee_data = {
            "user_id": test_employee_user.id,
            "employee_number": "EMP-TEST-001",
            "department": "Engineering",
            "position": "Senior Developer",
            "hire_date": "2024-01-15",
            "status": "ACTIVE"
        }
        response = await client.post(
            "/api/v1/employees/",
            json=employee_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["employee_number"] == employee_data["employee_number"]
        assert data["department"] == employee_data["department"]
    
    async def test_create_employee_duplicate_number(
        self,
        client: AsyncClient,
        test_employee_profile: EmployeeProfile,
        db_session: AsyncSession,
        auth_headers: dict
    ):
        """Test creating employee with duplicate employee number."""
        # Create another user
        from tera.modules.users.models import User, UserRole, UserStatus
        from tera.utils.security import hash_password
        
        new_user = User(
            email="another@test.com",
            username="anotheruser",
            first_name="Another",
            last_name="User",
            hashed_password=hash_password("testpass123"),
            role=UserRole.EMPLOYEE,
            status=UserStatus.ACTIVE,
            company_id=test_employee_profile.company_id
        )
        db_session.add(new_user)
        await db_session.commit()
        await db_session.refresh(new_user)
        
        employee_data = {
            "user_id": new_user.id,
            "employee_number": test_employee_profile.employee_number,
            "department": "HR",
            "position": "HR Manager",
            "hire_date": "2024-02-01"
        }
        response = await client.post(
            "/api/v1/employees/",
            json=employee_data,
            headers=auth_headers
        )
        assert response.status_code == 400
    
    async def test_list_employees(
        self,
        client: AsyncClient,
        test_employee_profile: EmployeeProfile,
        auth_headers: dict
    ):
        """Test listing employees."""
        response = await client.get("/api/v1/employees/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(e["employee_number"] == test_employee_profile.employee_number for e in data)
    
    async def test_get_employee_by_id(
        self,
        client: AsyncClient,
        test_employee_profile: EmployeeProfile,
        auth_headers: dict
    ):
        """Test getting employee by ID."""
        response = await client.get(
            f"/api/v1/employees/{test_employee_profile.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_employee_profile.id
        assert data["employee_number"] == test_employee_profile.employee_number
    
    async def test_get_employee_by_user_id(
        self,
        client: AsyncClient,
        test_employee_profile: EmployeeProfile,
        test_employee_user: User,
        auth_headers: dict
    ):
        """Test getting employee by user ID."""
        response = await client.get(
            f"/api/v1/employees/user/{test_employee_user.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_employee_user.id
    
    async def test_update_employee(
        self,
        client: AsyncClient,
        test_employee_profile: EmployeeProfile,
        auth_headers: dict
    ):
        """Test updating employee."""
        update_data = {
            "department": "Product",
            "position": "Lead Developer"
        }
        response = await client.patch(
            f"/api/v1/employees/{test_employee_profile.id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["department"] == "Product"
        assert data["position"] == "Lead Developer"
    
    async def test_delete_employee(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        auth_headers: dict
    ):
        """Test deleting employee."""
        # Create user and employee to delete
        from tera.modules.users.models import User, UserRole, UserStatus
        from tera.utils.security import hash_password
        
        user = User(
            email="todelete@test.com",
            username="todelete",
            first_name="To",
            last_name="Delete",
            hashed_password=hash_password("testpass123"),
            role=UserRole.EMPLOYEE,
            status=UserStatus.ACTIVE,
            company_id=test_company.id
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        employee = EmployeeProfile(
            user_id=user.id,
            company_id=test_company.id,
            employee_number="EMP-DEL-001",
            department="Temp",
            position="Temp Position",
            hire_date="2024-01-01",
            status=EmployeeStatus.ACTIVE
        )
        db_session.add(employee)
        await db_session.commit()
        await db_session.refresh(employee)
        
        response = await client.delete(
            f"/api/v1/employees/{employee.id}",
            headers=auth_headers
        )
        assert response.status_code == 204


class TestEmployeeStatusChanges:
    """Test employee status change operations."""
    
    async def test_deactivate_employee(
        self,
        client: AsyncClient,
        test_employee_profile: EmployeeProfile,
        auth_headers: dict
    ):
        """Test deactivating an employee."""
        response = await client.post(
            f"/api/v1/employees/{test_employee_profile.id}/deactivate",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "INACTIVE"
    
    async def test_reactivate_employee(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_employee_profile: EmployeeProfile,
        auth_headers: dict
    ):
        """Test reactivating an employee."""
        # First deactivate
        test_employee_profile.status = EmployeeStatus.INACTIVE
        await db_session.commit()
        
        response = await client.post(
            f"/api/v1/employees/{test_employee_profile.id}/reactivate",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ACTIVE"
    
    async def test_terminate_employee(
        self,
        client: AsyncClient,
        test_employee_profile: EmployeeProfile,
        auth_headers: dict
    ):
        """Test terminating an employee."""
        termination_data = {
            "termination_date": "2024-12-31",
            "termination_reason": "Resigned"
        }
        response = await client.post(
            f"/api/v1/employees/{test_employee_profile.id}/terminate",
            json=termination_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "TERMINATED"


class TestEmployeeFiltering:
    """Test employee filtering and search."""
    
    async def test_filter_by_department(
        self,
        client: AsyncClient,
        test_employee_profile: EmployeeProfile,
        auth_headers: dict
    ):
        """Test filtering employees by department."""
        response = await client.get(
            f"/api/v1/employees/?department={test_employee_profile.department}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert all(e["department"] == test_employee_profile.department for e in data)
    
    async def test_filter_by_status(
        self,
        client: AsyncClient,
        test_employee_profile: EmployeeProfile,
        auth_headers: dict
    ):
        """Test filtering employees by status."""
        response = await client.get(
            "/api/v1/employees/?status=ACTIVE",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert all(e["status"] == "ACTIVE" for e in data)


class TestEmployeeAuthorization:
    """Test employee authorization."""
    
    async def test_employee_cannot_create_employee(
        self,
        client: AsyncClient,
        test_employee_user: User,
        employee_auth_headers: dict
    ):
        """Test that regular employees cannot create employee profiles."""
        employee_data = {
            "user_id": test_employee_user.id,
            "employee_number": "EMP-UNAUTH-001",
            "department": "Engineering",
            "position": "Developer",
            "hire_date": "2024-01-01"
        }
        response = await client.post(
            "/api/v1/employees/",
            json=employee_data,
            headers=employee_auth_headers
        )
        assert response.status_code == 403
    
    async def test_hr_admin_can_create_employee(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        hr_auth_headers: dict
    ):
        """Test that HR admins can create employee profiles."""
        from tera.modules.users.models import User, UserRole, UserStatus
        from tera.utils.security import hash_password
        
        # Create a user first
        user = User(
            email="hremployee@test.com",
            username="hremployee",
            first_name="HR",
            last_name="Employee",
            hashed_password=hash_password("testpass123"),
            role=UserRole.EMPLOYEE,
            status=UserStatus.ACTIVE,
            company_id=test_company.id
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        employee_data = {
            "user_id": user.id,
            "employee_number": "EMP-HR-001",
            "department": "Sales",
            "position": "Sales Rep",
            "hire_date": "2024-01-01"
        }
        response = await client.post(
            "/api/v1/employees/",
            json=employee_data,
            headers=hr_auth_headers
        )
        assert response.status_code == 201
    
    async def test_employee_can_view_own_profile(
        self,
        client: AsyncClient,
        test_employee_profile: EmployeeProfile,
        test_employee_user: User,
        employee_auth_headers: dict
    ):
        """Test that employees can view their own profile."""
        response = await client.get(
            f"/api/v1/employees/user/{test_employee_user.id}",
            headers=employee_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_employee_user.id
