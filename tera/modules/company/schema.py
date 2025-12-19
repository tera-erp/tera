from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from .models import CompanyStatus

# Base schema with common fields
class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    legal_name: str = Field(..., min_length=1, max_length=255)
    country_code: str = Field(..., min_length=2, max_length=2)  # ISO 3166-1 alpha-2
    currency_code: str = Field(..., min_length=3, max_length=3)  # ISO 4217
    timezone: str = Field(default="UTC", max_length=50)

# Schema for creating a company
class CompanyCreate(CompanyBase):
    tax_id: Optional[str] = Field(None, max_length=100)
    registration_number: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state_province: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    fiscal_year_start_month: int = Field(default=1, ge=1, le=12)
    date_format: str = Field(default="DD/MM/YYYY", max_length=20)
    einvoice_enabled: bool = False
    einvoice_provider: Optional[str] = Field(None, max_length=100)
    einvoice_api_endpoint: Optional[str] = Field(None, max_length=500)
    logo_url: Optional[str] = Field(None, max_length=500)
    status: CompanyStatus = CompanyStatus.ACTIVE

# Schema for updating a company
class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    legal_name: Optional[str] = Field(None, min_length=1, max_length=255)
    country_code: Optional[str] = Field(None, min_length=2, max_length=2)
    currency_code: Optional[str] = Field(None, min_length=3, max_length=3)
    timezone: Optional[str] = Field(None, max_length=50)
    tax_id: Optional[str] = Field(None, max_length=100)
    registration_number: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state_province: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    fiscal_year_start_month: Optional[int] = Field(None, ge=1, le=12)
    date_format: Optional[str] = Field(None, max_length=20)
    einvoice_enabled: Optional[bool] = None
    einvoice_provider: Optional[str] = Field(None, max_length=100)
    einvoice_api_endpoint: Optional[str] = Field(None, max_length=500)
    logo_url: Optional[str] = Field(None, max_length=500)
    status: Optional[CompanyStatus] = None

# Schema for company response
class CompanyResponse(CompanyBase):
    id: int
    tax_id: Optional[str] = None
    registration_number: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    fiscal_year_start_month: int
    date_format: str
    einvoice_enabled: bool
    einvoice_provider: Optional[str] = None
    einvoice_api_endpoint: Optional[str] = None
    logo_url: Optional[str] = None
    status: CompanyStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Schema for company list (simplified)
class CompanyListItem(BaseModel):
    id: int
    name: str
    country_code: str
    currency_code: str
    status: CompanyStatus

    model_config = ConfigDict(from_attributes=True)
