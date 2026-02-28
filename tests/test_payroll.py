"""Tests for the payroll module."""
import pytest
from datetime import datetime
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tera.modules.users.models import User
from tera.modules.company.models import Company
from tera.modules.employees.models import EmployeeProfile
from tera.modules.payroll.models import PayrollRun, Payslip


class TestPayrollRunCRUD:
    """Test payroll run CRUD operations."""
    
    async def test_create_payroll_run(
        self,
        client: AsyncClient,
        test_company: Company,
        auth_headers: dict
    ):
        """Test creating a payroll run."""
        run_data = {
            "company_id": test_company.id,
            "period_name": "January 2024",
            "employee_count": 10,
            "total_gross": 50000.0,
            "total_deductions": 5000.0,
            "total_net": 45000.0,
            "notes": "Regular monthly payroll"
        }
        response = await client.post(
            "/api/v1/payroll/runs/",
            json=run_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["period_name"] == run_data["period_name"]
        assert data["employee_count"] == run_data["employee_count"]
    
    async def test_list_payroll_runs(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        auth_headers: dict
    ):
        """Test listing payroll runs."""
        # Create test payroll runs
        run1 = PayrollRun(
            company_id=test_company.id,
            period_name="Jan 2024",
            state="DRAFT",
            employee_count=5,
            total_gross=25000.0,
            total_deductions=2500.0,
            total_net=22500.0,
            run_date=datetime.now()
        )
        run2 = PayrollRun(
            company_id=test_company.id,
            period_name="Feb 2024",
            state="DRAFT",
            employee_count=5,
            total_gross=26000.0,
            total_deductions=2600.0,
            total_net=23400.0,
            run_date=datetime.now()
        )
        db_session.add_all([run1, run2])
        await db_session.commit()
        
        response = await client.get("/api/v1/payroll/runs/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
    
    async def test_get_payroll_run_by_id(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        auth_headers: dict
    ):
        """Test getting payroll run by ID."""
        run = PayrollRun(
            company_id=test_company.id,
            period_name="March 2024",
            state="DRAFT",
            employee_count=8,
            total_gross=40000.0,
            total_deductions=4000.0,
            total_net=36000.0,
            run_date=datetime.now()
        )
        db_session.add(run)
        await db_session.commit()
        await db_session.refresh(run)
        
        response = await client.get(
            f"/api/v1/payroll/runs/{run.id}/",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == run.id
        assert data["period_name"] == "March 2024"
    
    async def test_update_payroll_run(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        auth_headers: dict
    ):
        """Test updating payroll run."""
        run = PayrollRun(
            company_id=test_company.id,
            period_name="April 2024",
            state="DRAFT",
            employee_count=10,
            total_gross=50000.0,
            total_deductions=5000.0,
            total_net=45000.0,
            run_date=datetime.now()
        )
        db_session.add(run)
        await db_session.commit()
        await db_session.refresh(run)
        
        update_data = {
            "period_name": "April 2024 - Revised",
            "notes": "Updated with corrections"
        }
        response = await client.put(
            f"/api/v1/payroll/runs/{run.id}/",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["period_name"] == "April 2024 - Revised"


class TestPayrollRunStateMachine:
    """Test payroll run state transitions."""
    
    async def test_process_payroll_run(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        auth_headers: dict
    ):
        """Test processing a payroll run."""
        run = PayrollRun(
            company_id=test_company.id,
            period_name="May 2024",
            state="DRAFT",
            employee_count=5,
            total_gross=25000.0,
            total_deductions=2500.0,
            total_net=22500.0,
            run_date=datetime.now()
        )
        db_session.add(run)
        await db_session.commit()
        await db_session.refresh(run)
        
        response = await client.post(
            f"/api/v1/payroll/runs/{run.id}/process",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["status"] == "PROCESSED"
    
    async def test_complete_payroll_run(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        auth_headers: dict
    ):
        """Test completing a payroll run."""
        run = PayrollRun(
            company_id=test_company.id,
            period_name="June 2024",
            state="PROCESSED",
            employee_count=5,
            total_gross=25000.0,
            total_deductions=2500.0,
            total_net=22500.0,
            run_date=datetime.now()
        )
        db_session.add(run)
        await db_session.commit()
        await db_session.refresh(run)
        
        response = await client.post(
            f"/api/v1/payroll/runs/{run.id}/complete",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["status"] == "COMPLETED"
    
    async def test_release_payroll_run(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        auth_headers: dict
    ):
        """Test releasing a payroll run."""
        run = PayrollRun(
            company_id=test_company.id,
            period_name="July 2024",
            state="COMPLETED",
            employee_count=5,
            total_gross=25000.0,
            total_deductions=2500.0,
            total_net=22500.0,
            run_date=datetime.now()
        )
        db_session.add(run)
        await db_session.commit()
        await db_session.refresh(run)
        
        response = await client.post(
            f"/api/v1/payroll/runs/{run.id}/release",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["status"] == "RELEASED"
    
    async def test_revert_payroll_run(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        auth_headers: dict
    ):
        """Test reverting a payroll run."""
        run = PayrollRun(
            company_id=test_company.id,
            period_name="August 2024",
            state="PROCESSED",
            employee_count=5,
            total_gross=25000.0,
            total_deductions=2500.0,
            total_net=22500.0,
            run_date=datetime.now()
        )
        db_session.add(run)
        await db_session.commit()
        await db_session.refresh(run)
        
        response = await client.post(
            f"/api/v1/payroll/runs/{run.id}/revert",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["status"] == "DRAFT"


class TestPayslips:
    """Test payslip operations."""
    
    async def test_list_payslips(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_employee_profile: EmployeeProfile,
        auth_headers: dict
    ):
        """Test listing payslips."""
        # Create a payroll run and payslip
        run = PayrollRun(
            company_id=test_company.id,
            period_name="September 2024",
            state="RELEASED",
            employee_count=1,
            total_gross=5000.0,
            total_deductions=500.0,
            total_net=4500.0,
            run_date=datetime.now()
        )
        db_session.add(run)
        await db_session.commit()
        await db_session.refresh(run)
        
        payslip = Payslip(
            payroll_run_id=run.id,
            employee_id=test_employee_profile.id,
            period_name="September 2024",
            gross_salary=5000.0,
            total_deductions=500.0,
            net_salary=4500.0,
            payment_status="PENDING"
        )
        db_session.add(payslip)
        await db_session.commit()
        
        response = await client.get("/api/v1/payroll/payslips/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    async def test_get_payslip_by_id(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_employee_profile: EmployeeProfile,
        auth_headers: dict
    ):
        """Test getting payslip by ID."""
        run = PayrollRun(
            company_id=test_company.id,
            period_name="October 2024",
            state="RELEASED",
            employee_count=1,
            total_gross=5200.0,
            total_deductions=520.0,
            total_net=4680.0,
            run_date=datetime.now()
        )
        db_session.add(run)
        await db_session.commit()
        await db_session.refresh(run)
        
        payslip = Payslip(
            payroll_run_id=run.id,
            employee_id=test_employee_profile.id,
            period_name="October 2024",
            gross_salary=5200.0,
            total_deductions=520.0,
            net_salary=4680.0,
            payment_status="PENDING"
        )
        db_session.add(payslip)
        await db_session.commit()
        await db_session.refresh(payslip)
        
        response = await client.get(
            f"/api/v1/payroll/payslips/{payslip.id}/",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == payslip.id
        assert data["period_name"] == "October 2024"
    
    async def test_get_payslips_by_run(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_employee_profile: EmployeeProfile,
        auth_headers: dict
    ):
        """Test getting payslips for a specific run."""
        run = PayrollRun(
            company_id=test_company.id,
            period_name="November 2024",
            state="RELEASED",
            employee_count=1,
            total_gross=5300.0,
            total_deductions=530.0,
            total_net=4770.0,
            run_date=datetime.now()
        )
        db_session.add(run)
        await db_session.commit()
        await db_session.refresh(run)
        
        payslip = Payslip(
            payroll_run_id=run.id,
            employee_id=test_employee_profile.id,
            period_name="November 2024",
            gross_salary=5300.0,
            total_deductions=530.0,
            net_salary=4770.0,
            payment_status="PENDING"
        )
        db_session.add(payslip)
        await db_session.commit()
        
        response = await client.get(
            f"/api/v1/payroll/runs/{run.id}/payslips/",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(p["period_name"] == "November 2024" for p in data)


class TestPayrollCalculations:
    """Test payroll calculation endpoints."""
    
    async def test_calculate_preview_indonesia(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test payroll calculation preview for Indonesia."""
        preview_data = {
            "country_code": "IDN",
            "gross_salary": 10000000.0,
            "age": 30,
            "ptkp_status": "TK0"
        }
        response = await client.post(
            "/api/v1/payroll/calculate-preview",
            json=preview_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "gross_salary" in data
        assert "total_deductions" in data
        assert "net_salary" in data
    
    async def test_calculate_preview_singapore(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test payroll calculation preview for Singapore."""
        preview_data = {
            "country_code": "SGP",
            "gross_salary": 5000.0,
            "age": 28,
            "is_resident": True
        }
        response = await client.post(
            "/api/v1/payroll/calculate-preview",
            json=preview_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "gross_salary" in data
        assert "total_deductions" in data
        assert "net_salary" in data
    
    async def test_calculate_preview_invalid_country(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test payroll calculation with invalid country code."""
        preview_data = {
            "country_code": "XXX",
            "gross_salary": 5000.0,
            "age": 30
        }
        response = await client.post(
            "/api/v1/payroll/calculate-preview",
            json=preview_data,
            headers=auth_headers
        )
        assert response.status_code in [400, 422]


class TestPayrollAuthorization:
    """Test payroll authorization."""
    
    async def test_employee_cannot_create_payroll_run(
        self,
        client: AsyncClient,
        test_company: Company,
        employee_auth_headers: dict
    ):
        """Test that employees cannot create payroll runs."""
        run_data = {
            "company_id": test_company.id,
            "period_name": "December 2024",
            "employee_count": 5,
            "total_gross": 25000.0,
            "total_deductions": 2500.0,
            "total_net": 22500.0
        }
        response = await client.post(
            "/api/v1/payroll/runs/",
            json=run_data,
            headers=employee_auth_headers
        )
        assert response.status_code == 403
    
    async def test_hr_admin_can_create_payroll_run(
        self,
        client: AsyncClient,
        test_company: Company,
        hr_auth_headers: dict
    ):
        """Test that HR admins can create payroll runs."""
        run_data = {
            "company_id": test_company.id,
            "period_name": "December 2024",
            "employee_count": 5,
            "total_gross": 25000.0,
            "total_deductions": 2500.0,
            "total_net": 22500.0
        }
        response = await client.post(
            "/api/v1/payroll/runs/",
            json=run_data,
            headers=hr_auth_headers
        )
        assert response.status_code == 201
