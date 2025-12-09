from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.employee import EmploymentStatus, EmploymentType, PTKPStatus

# Base schema with common fields
class EmployeeProfileBase(BaseModel):
    employee_number: str = Field(..., min_length=1, max_length=50)
    department: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    job_title: Optional[str] = Field(None, max_length=100)
    employment_status: EmploymentStatus = EmploymentStatus.ACTIVE
    employment_type: EmploymentType = EmploymentType.FULL_TIME

# Schema for creating an employee profile
class EmployeeProfileCreate(EmployeeProfileBase):
    user_id: int
    company_id: int
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=20)
    nationality: Optional[str] = Field(None, max_length=50)
    national_id: Optional[str] = Field(None, max_length=100)
    personal_email: Optional[EmailStr] = None
    mobile_phone: Optional[str] = Field(None, max_length=50)
    emergency_contact_name: Optional[str] = Field(None, max_length=255)
    emergency_contact_phone: Optional[str] = Field(None, max_length=50)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state_province: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    hire_date: Optional[date] = None
    probation_end_date: Optional[date] = None
    manager_id: Optional[int] = None
    base_salary: Optional[float] = None
    salary_currency: Optional[str] = Field(None, max_length=3)
    tax_id: Optional[str] = Field(None, max_length=100)
    ptkp_status: Optional[PTKPStatus] = None
    is_tax_resident: bool = True
    social_security_number: Optional[str] = Field(None, max_length=100)
    bank_name: Optional[str] = Field(None, max_length=100)
    bank_account_number: Optional[str] = Field(None, max_length=100)
    bank_account_holder: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None

# Schema for updating an employee profile
class EmployeeProfileUpdate(BaseModel):
    employee_number: Optional[str] = Field(None, min_length=1, max_length=50)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=20)
    nationality: Optional[str] = Field(None, max_length=50)
    national_id: Optional[str] = Field(None, max_length=100)
    personal_email: Optional[EmailStr] = None
    mobile_phone: Optional[str] = Field(None, max_length=50)
    emergency_contact_name: Optional[str] = Field(None, max_length=255)
    emergency_contact_phone: Optional[str] = Field(None, max_length=50)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state_province: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    employment_status: Optional[EmploymentStatus] = None
    employment_type: Optional[EmploymentType] = None
    department: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    job_title: Optional[str] = Field(None, max_length=100)
    hire_date: Optional[date] = None
    probation_end_date: Optional[date] = None
    termination_date: Optional[date] = None
    manager_id: Optional[int] = None
    base_salary: Optional[float] = None
    salary_currency: Optional[str] = Field(None, max_length=3)
    tax_id: Optional[str] = Field(None, max_length=100)
    ptkp_status: Optional[PTKPStatus] = None
    is_tax_resident: Optional[bool] = None
    social_security_number: Optional[str] = Field(None, max_length=100)
    bank_name: Optional[str] = Field(None, max_length=100)
    bank_account_number: Optional[str] = Field(None, max_length=100)
    bank_account_holder: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None

# Schema for employee profile response
class EmployeeProfileResponse(EmployeeProfileBase):
    id: int
    user_id: int
    company_id: int
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    national_id: Optional[str] = None
    personal_email: Optional[str] = None
    mobile_phone: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    hire_date: Optional[date] = None
    probation_end_date: Optional[date] = None
    termination_date: Optional[date] = None
    manager_id: Optional[int] = None
    base_salary: Optional[float] = None
    salary_currency: Optional[str] = None
    tax_id: Optional[str] = None
    ptkp_status: Optional[PTKPStatus] = None
    is_tax_resident: bool
    social_security_number: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_account_holder: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
