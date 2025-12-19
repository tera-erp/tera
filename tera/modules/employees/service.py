"""
Employee Service - Contract/Interface for cross-module interactions.

This service provides a clean interface for other modules (like payroll)
to interact with employee data without tight coupling.
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import EmployeeProfile, EmploymentStatus


class EmployeeService:
    """
    Service layer for employee operations.
    
    This provides a contract that other modules can use to interact
    with employee data in a clean, decoupled way.
    """
    
    @staticmethod
    async def get_employee_by_id(
        db: AsyncSession,
        employee_id: int
    ) -> Optional[EmployeeProfile]:
        """Get employee by ID."""
        result = await db.execute(
            select(EmployeeProfile).where(EmployeeProfile.id == employee_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_employees_by_company(
        db: AsyncSession,
        company_id: int,
        status: Optional[EmploymentStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[EmployeeProfile]:
        """Get all employees for a company, optionally filtered by status."""
        query = select(EmployeeProfile).where(
            EmployeeProfile.company_id == company_id
        )
        
        if status:
            query = query.where(EmployeeProfile.employment_status == status)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_active_employees(
        db: AsyncSession,
        company_id: int
    ) -> List[EmployeeProfile]:
        """Get all active employees for a company."""
        return await EmployeeService.get_employees_by_company(
            db=db,
            company_id=company_id,
            status=EmploymentStatus.ACTIVE
        )
    
    @staticmethod
    async def get_employee_by_number(
        db: AsyncSession,
        company_id: int,
        employee_number: str
    ) -> Optional[EmployeeProfile]:
        """Get employee by employee number within a company."""
        result = await db.execute(
            select(EmployeeProfile).where(
                EmployeeProfile.company_id == company_id,
                EmployeeProfile.employee_number == employee_number
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def is_employee_active(
        db: AsyncSession,
        employee_id: int
    ) -> bool:
        """Check if an employee is active."""
        employee = await EmployeeService.get_employee_by_id(db, employee_id)
        if not employee:
            return False
        return employee.employment_status == EmploymentStatus.ACTIVE
    
    @staticmethod
    async def get_employee_salary_info(
        db: AsyncSession,
        employee_id: int
    ) -> Optional[dict]:
        """
        Get employee salary information.
        
        Returns a dict with salary details or None if employee not found.
        """
        employee = await EmployeeService.get_employee_by_id(db, employee_id)
        if not employee:
            return None
        
        return {
            "employee_id": employee.id,
            "employee_number": employee.employee_number,
            "base_salary": float(employee.base_salary) if employee.base_salary else 0.0,
            "salary_currency": employee.salary_currency or "USD",
            "salary_type": employee.salary_type or "monthly",
            "bank_account_number": employee.bank_account_number,
            "bank_account_holder": employee.bank_account_holder,
            "bank_name": employee.bank_name,
        }
    
    @staticmethod
    async def count_employees_by_company(
        db: AsyncSession,
        company_id: int,
        status: Optional[EmploymentStatus] = None
    ) -> int:
        """Count employees in a company, optionally filtered by status."""
        from sqlalchemy import func
        
        query = select(func.count(EmployeeProfile.id)).where(
            EmployeeProfile.company_id == company_id
        )
        
        if status:
            query = query.where(EmployeeProfile.employment_status == status)
        
        result = await db.execute(query)
        return result.scalar() or 0
