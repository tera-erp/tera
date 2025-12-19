from typing import Optional
from datetime import date
from pydantic import BaseModel
from .models import EmploymentStatus, EmploymentType

class EmployeeProfileBase(BaseModel):
    user_id: int
    company_id: int
    employee_number: str
    employment_status: str = EmploymentStatus.ACTIVE
    employment_type: str = EmploymentType.FULL_TIME
    hire_date: date


class EmployeeProfileCreate(EmployeeProfileBase):
    pass


class EmployeeProfileUpdate(BaseModel):
    employment_status: Optional[str] = None
    employment_type: Optional[str] = None
    hire_date: Optional[date] = None
    termination_date: Optional[date] = None


class EmployeeProfileResponse(EmployeeProfileBase):
    id: int
    termination_date: Optional[date] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
