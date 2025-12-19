from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class InvoiceLineCreate(BaseModel):
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    quantity: Decimal = Field(gt=0)
    price_unit: Decimal = Field(gt=0)
    description: Optional[str] = None


class InvoiceLineUpdate(BaseModel):
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    quantity: Optional[Decimal] = None
    price_unit: Optional[Decimal] = None
    description: Optional[str] = None


class InvoiceCreate(BaseModel):
    """Schema for creating a new invoice."""
    customer_id: int
    invoice_date: Optional[datetime] = None
    currency_code: str = "USD"
    amount_untaxed: Decimal = Decimal(0)
    amount_tax: Decimal = Decimal(0)
    amount_total: Decimal = Decimal(0)
    notes: Optional[str] = None
    line_items: Optional[List[InvoiceLineCreate]] = []


class InvoiceUpdate(BaseModel):
    """Schema for updating an invoice."""
    customer_id: Optional[int] = None
    invoice_date: Optional[datetime] = None
    currency_code: Optional[str] = None
    amount_untaxed: Optional[Decimal] = None
    amount_tax: Optional[Decimal] = None
    amount_total: Optional[Decimal] = None
    notes: Optional[str] = None
    line_items: Optional[List[InvoiceLineUpdate]] = None


class InvoiceLine(BaseModel):
    product_name: str
    qty: Decimal = Field(gt=0)
    unit_price: Decimal = Field(gt=0)
    amount: Decimal
    description: Optional[str] = None


class Invoice(BaseModel):
    id: int
    invoice_number: str
    customer_name: str
    status: str
    total: Decimal
    invoice_date: str
    line_items: List[InvoiceLine]


class InvoiceActionResponse(BaseModel):
    success: bool
    message: str
    status: str


class CustomerResponse(BaseModel):
    """Response for customer/partner list."""
    id: int
    name: str
    country_code: str
    email: Optional[str] = None
    phone: Optional[str] = None
    tax_id: Optional[str] = None
    address: Optional[str] = None

    class Config:
        from_attributes = True


class CustomerCreate(BaseModel):
    name: str
    country_code: str = Field(..., min_length=3, max_length=3)
    email: Optional[str] = None
    phone: Optional[str] = None
    tax_id: Optional[str] = None
    address: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    country_code: Optional[str] = Field(default=None, min_length=3, max_length=3)
    email: Optional[str] = None
    phone: Optional[str] = None
    tax_id: Optional[str] = None
    address: Optional[str] = None