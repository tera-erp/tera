from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Date, DateTime, ForeignKey, Numeric, Text, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum

class EmploymentStatus(str, enum.Enum):
    """Employment status"""
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    PROBATION = "probation"
    TERMINATED = "terminated"
    RESIGNED = "resigned"
    SUSPENDED = "suspended"

class EmploymentType(str, enum.Enum):
    """Employment type"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERN = "intern"
    CONSULTANT = "consultant"
    TEMPORARY = "temporary"

class MaritalStatus(str, enum.Enum):
    """Marital status"""
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"

class Gender(str, enum.Enum):
    """Gender"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class PTKPStatus(str, enum.Enum):
    """PTKP Status for Indonesian Tax (Penghasilan Tidak Kena Pajak)"""
    TK0 = "TK/0"  # Single, no dependents
    TK1 = "TK/1"  # Single, 1 dependent
    TK2 = "TK/2"  # Single, 2 dependents
    TK3 = "TK/3"  # Single, 3 dependents
    K0 = "K/0"    # Married, no dependents
    K1 = "K/1"    # Married, 1 dependent
    K2 = "K/2"    # Married, 2 dependents
    K3 = "K/3"    # Married, 3 dependents

class EmployeeProfile(Base):
    __tablename__ = "employee_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # User and Company Association
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    
    # Employee Identification
    employee_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Personal Information
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date)
    gender: Mapped[Optional[Gender]] = mapped_column(SQLEnum(Gender))
    marital_status: Mapped[Optional[MaritalStatus]] = mapped_column(SQLEnum(MaritalStatus))
    nationality: Mapped[Optional[str]] = mapped_column(String(50))
    national_id: Mapped[Optional[str]] = mapped_column(String(100))  # SSN, NRIC, NIK, etc.
    passport_number: Mapped[Optional[str]] = mapped_column(String(100))
    passport_expiry: Mapped[Optional[date]] = mapped_column(Date)
    work_permit_number: Mapped[Optional[str]] = mapped_column(String(100))
    work_permit_expiry: Mapped[Optional[date]] = mapped_column(Date)
    
    # Contact Details
    personal_email: Mapped[Optional[str]] = mapped_column(String(255))
    mobile_phone: Mapped[Optional[str]] = mapped_column(String(50))
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(255))
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Address
    address_line1: Mapped[Optional[str]] = mapped_column(String(255))
    address_line2: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state_province: Mapped[Optional[str]] = mapped_column(String(100))
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    country: Mapped[Optional[str]] = mapped_column(String(2))  # ISO 3166-1 alpha-2
    
    # Employment Details
    employment_status: Mapped[EmploymentStatus] = mapped_column(
        SQLEnum(EmploymentStatus), 
        default=EmploymentStatus.ACTIVE, 
        nullable=False
    )
    employment_type: Mapped[EmploymentType] = mapped_column(
        SQLEnum(EmploymentType), 
        default=EmploymentType.FULL_TIME, 
        nullable=False
    )
    department: Mapped[Optional[str]] = mapped_column(String(100))
    position: Mapped[Optional[str]] = mapped_column(String(100))
    job_title: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Dates
    hire_date: Mapped[Optional[date]] = mapped_column(Date)
    probation_end_date: Mapped[Optional[date]] = mapped_column(Date)
    termination_date: Mapped[Optional[date]] = mapped_column(Date)
    
    # Reporting
    manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey("employee_profiles.id"))
    
    # Compensation
    base_salary: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    salary_currency: Mapped[Optional[str]] = mapped_column(String(3), default="USD")
    salary_type: Mapped[Optional[str]] = mapped_column(String(20), default="monthly")  # monthly, hourly, daily
    hourly_rate: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    
    # Allowances
    transport_allowance: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), default=0)
    meal_allowance: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), default=0)
    housing_allowance: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), default=0)
    other_allowances: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), default=0)
    
    # Tax Information (Country-specific)
    tax_id: Mapped[Optional[str]] = mapped_column(String(100))  # TIN, NPWP, etc.
    ptkp_status: Mapped[Optional[PTKPStatus]] = mapped_column(SQLEnum(PTKPStatus))  # For Indonesian employees
    is_tax_resident: Mapped[bool] = mapped_column(default=True, nullable=False)
    tax_exemption: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    # Social Security Numbers (Country-specific)
    social_security_number: Mapped[Optional[str]] = mapped_column(String(100))
    # Indonesia: BPJS Kesehatan & Ketenagakerjaan
    bpjs_kesehatan_number: Mapped[Optional[str]] = mapped_column(String(100))
    bpjs_ketenagakerjaan_number: Mapped[Optional[str]] = mapped_column(String(100))
    # Malaysia: EPF & SOCSO
    epf_number: Mapped[Optional[str]] = mapped_column(String(100))
    socso_number: Mapped[Optional[str]] = mapped_column(String(100))
    # Singapore: CPF
    cpf_number: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Bank Details for Payroll
    bank_name: Mapped[Optional[str]] = mapped_column(String(100))
    bank_account_number: Mapped[Optional[str]] = mapped_column(String(100))
    bank_account_holder: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="employee_profile")
    company: Mapped["Company"] = relationship("Company", back_populates="employee_profiles")
    manager: Mapped[Optional["EmployeeProfile"]] = relationship(
        "EmployeeProfile",
        remote_side=[id],
        foreign_keys=[manager_id]
    )

    def __repr__(self) -> str:
        return f"<EmployeeProfile(id={self.id}, employee_number={self.employee_number})>"
