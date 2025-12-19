"""Payroll module models.
PayrollRun, Payslip, and related components for comprehensive payroll management.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime, Text, Date, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, date
from typing import Optional
from tera.core.database import Base
import enum


class PayrollRunState(str, enum.Enum):
    """Payroll run states"""
    DRAFT = "draft"
    PROCESSING = "processing"
    CALCULATED = "calculated"
    APPROVED = "approved"
    PAID = "paid"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    """Payment status for payslips"""
    PENDING = "pending"
    PROCESSING = "processing"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LeaveType(str, enum.Enum):
    """Leave types"""
    ANNUAL = "annual"
    SICK = "sick"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    UNPAID = "unpaid"
    COMPASSIONATE = "compassionate"
    STUDY = "study"
    OTHER = "other"


class LeaveStatus(str, enum.Enum):
    """Leave request statuses"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class PayrollRun(Base):
    __tablename__ = "payroll_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    
    # Period Information
    run_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    period_name: Mapped[str] = mapped_column(String(100), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    payment_date: Mapped[Optional[date]] = mapped_column(Date)
    
    # State Management
    state: Mapped[PayrollRunState] = mapped_column(String(50), default=PayrollRunState.DRAFT, nullable=False, index=True)
    
    # Summary Fields
    employee_count: Mapped[int] = mapped_column(default=0, nullable=False)
    total_gross: Mapped[float] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    total_allowances: Mapped[float] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    total_deductions: Mapped[float] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    total_employer_contributions: Mapped[float] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    total_net: Mapped[float] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    
    # Processing Info
    calculated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    calculated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    approved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    payslips: Mapped[list["Payslip"]] = relationship("Payslip", back_populates="payroll_run", cascade="all, delete-orphan")


class Payslip(Base):
    __tablename__ = "payroll_payslips"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    payroll_run_id: Mapped[int] = mapped_column(ForeignKey("payroll_runs.id"), nullable=False, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee_profiles.id"), nullable=False, index=True)
    
    # Period Information
    payslip_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    period_name: Mapped[str] = mapped_column(String(100), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Salary Components
    base_salary: Mapped[float] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    worked_days: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    total_days: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    
    # Allowances (stored as JSON for flexibility)
    allowances: Mapped[Optional[dict]] = mapped_column(JSON)
    total_allowances: Mapped[float] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    
    # Overtime
    overtime_hours: Mapped[float] = mapped_column(Numeric(8, 2), default=0, nullable=False)
    overtime_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    
    # Gross Pay
    gross_salary: Mapped[float] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    
    # Deductions (stored as JSON for flexibility)
    deductions: Mapped[Optional[dict]] = mapped_column(JSON)
    total_deductions: Mapped[float] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    
    # Employer Contributions (informational)
    employer_contributions: Mapped[Optional[dict]] = mapped_column(JSON)
    total_employer_contributions: Mapped[float] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    
    # Net Pay
    net_salary: Mapped[float] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    
    # Payment Information
    payment_status: Mapped[PaymentStatus] = mapped_column(String(50), default=PaymentStatus.PENDING, nullable=False, index=True)
    payment_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    payment_method: Mapped[Optional[str]] = mapped_column(String(50))
    payment_reference: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    payroll_run: Mapped["PayrollRun"] = relationship("PayrollRun", back_populates="payslips")


class LeaveBalance(Base):
    __tablename__ = "leave_balances"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee_profiles.id"), nullable=False, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    
    # Leave Type
    leave_type: Mapped[LeaveType] = mapped_column(String(50), nullable=False)
    year: Mapped[int] = mapped_column(nullable=False, index=True)
    
    # Balances
    entitled_days: Mapped[float] = mapped_column(Numeric(8, 2), default=0, nullable=False)
    used_days: Mapped[float] = mapped_column(Numeric(8, 2), default=0, nullable=False)
    pending_days: Mapped[float] = mapped_column(Numeric(8, 2), default=0, nullable=False)
    remaining_days: Mapped[float] = mapped_column(Numeric(8, 2), default=0, nullable=False)
    
    # Carryover
    carried_forward: Mapped[float] = mapped_column(Numeric(8, 2), default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee_profiles.id"), nullable=False, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    
    # Request Details
    request_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    leave_type: Mapped[LeaveType] = mapped_column(String(50), nullable=False)
    
    # Dates
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_days: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    
    # Details
    reason: Mapped[Optional[str]] = mapped_column(Text)
    attachment_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Status
    status: Mapped[LeaveStatus] = mapped_column(String(50), default=LeaveStatus.DRAFT, nullable=False, index=True)
    
    # Approval Flow
    approver_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Attendance(Base):
    __tablename__ = "attendance_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee_profiles.id"), nullable=False, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    
    # Date and Time
    attendance_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    clock_in: Mapped[Optional[datetime]] = mapped_column(DateTime)
    clock_out: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Hours
    worked_hours: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    overtime_hours: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    break_hours: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    
    # Status
    is_present: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_late: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_holiday: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
