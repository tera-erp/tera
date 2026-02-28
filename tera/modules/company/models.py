from datetime import datetime
from datetime import timezone as tz
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from tera.core.database import Base
from tera.modules.employees.models import EmployeeProfile


class CompanyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    legal_name = Column(String(255), nullable=False)
    country_code = Column(String(3), nullable=False)
    currency_code = Column(String(3), nullable=False, default="USD")
    timezone = Column(String(50), nullable=False, default="UTC")
    status = Column(SQLEnum(CompanyStatus),
                    nullable=False,
                    default=CompanyStatus.ACTIVE)

    # Additional company information
    tax_id = Column(String(100), nullable=True)
    registration_number = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state_province = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)

    # Financial and localization settings
    fiscal_year_start_month = Column(Integer, nullable=False, default=1)
    date_format = Column(String(20), nullable=False, default="DD/MM/YYYY")

    # E-invoice settings
    einvoice_enabled = Column(Boolean, nullable=False, default=False)
    einvoice_provider = Column(String(100), nullable=True)
    einvoice_api_endpoint = Column(String(500), nullable=True)

    # Branding
    logo_url = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.now(tz.utc))
    updated_at = Column(DateTime,
                        default=datetime.now(tz.utc),
                        onupdate=datetime.now(tz.utc))

    # Relationships
    users = relationship("User", back_populates="company")
    employee_profiles = relationship(EmployeeProfile, back_populates="company")
