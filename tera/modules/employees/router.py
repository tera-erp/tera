from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from tera.core.database import get_db
from tera.modules.users.models import User
from .models import EmployeeProfile
from .schema import (
    EmployeeProfileCreate,
    EmployeeProfileUpdate,
    EmployeeProfileResponse
)
from datetime import datetime

router = APIRouter(prefix="/employees", tags=["employees"])

@router.post("/", response_model=EmployeeProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_employee_profile(
    employee_data: EmployeeProfileCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new employee profile"""
    # Check if user exists
    result = await db.execute(
        select(User).where(User.id == employee_data.user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if employee profile already exists for this user
    result = await db.execute(
        select(EmployeeProfile).where(EmployeeProfile.user_id == employee_data.user_id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee profile already exists for this user"
        )
    
    # Check if employee number is unique within company
    result = await db.execute(
        select(EmployeeProfile).where(
            EmployeeProfile.company_id == employee_data.company_id,
            EmployeeProfile.employee_number == employee_data.employee_number
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee number already exists in this company"
        )
    
    # Create new employee profile
    employee = EmployeeProfile(**employee_data.model_dump())
    
    db.add(employee)
    await db.commit()
    await db.refresh(employee)
    
    return employee

@router.get("/", response_model=List[EmployeeProfileResponse])
async def list_employees(
    company_id: int = None,
    employment_status: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all employee profiles, optionally filtered by company or status"""
    query = select(EmployeeProfile)
    
    if company_id:
        query = query.where(EmployeeProfile.company_id == company_id)
    
    if employment_status:
        query = query.where(EmployeeProfile.employment_status == employment_status)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    employees = result.scalars().all()
    
    return employees

@router.get("/{employee_id}", response_model=EmployeeProfileResponse)
async def get_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific employee profile by ID"""
    result = await db.execute(
        select(EmployeeProfile).where(EmployeeProfile.id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    return employee

@router.get("/user/{user_id}", response_model=EmployeeProfileResponse)
async def get_employee_by_user_id(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get employee profile by user ID"""
    result = await db.execute(
        select(EmployeeProfile).where(EmployeeProfile.user_id == user_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found for this user"
        )
    
    return employee

@router.patch("/{employee_id}", response_model=EmployeeProfileResponse)
async def update_employee(
    employee_id: int,
    employee_data: EmployeeProfileUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an employee profile"""
    result = await db.execute(
        select(EmployeeProfile).where(EmployeeProfile.id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    # Update fields
    update_data = employee_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(employee, field, value)
    
    employee.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(employee)
    
    return employee

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an employee profile"""
    result = await db.execute(
        select(EmployeeProfile).where(EmployeeProfile.id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    await db.delete(employee)
    await db.commit()
    
    return None
