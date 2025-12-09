from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Text, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum

class CompanyStatus(str, enum.Enum):
    """Company status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Localization
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, index=True)  # ISO 3166-1 alpha-2
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)  # ISO 4217
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    
    # Registration Details
    tax_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)  # Tax ID / VAT Number
    registration_number: Mapped[Optional[str]] = mapped_column(String(100))  # Business registration number
    
    # Contact Information
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    website: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Address
    address_line1: Mapped[Optional[str]] = mapped_column(String(255))
    address_line2: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state_province: Mapped[Optional[str]] = mapped_column(String(100))
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Business Settings
    fiscal_year_start_month: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1 = January
    date_format: Mapped[str] = mapped_column(String(20), default="DD/MM/YYYY", nullable=False)
    
    # E-Invoice Settings
    einvoice_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    einvoice_provider: Mapped[Optional[str]] = mapped_column(String(100))
    einvoice_api_endpoint: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Logo and Branding
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Status
    status: Mapped[CompanyStatus] = mapped_column(SQLEnum(CompanyStatus), default=CompanyStatus.ACTIVE, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="company", cascade="all, delete-orphan")
    employee_profiles: Mapped[List["EmployeeProfile"]] = relationship(
        "EmployeeProfile", 
        back_populates="company",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name={self.name}, country={self.country_code})>"
