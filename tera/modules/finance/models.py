"""Finance module models.
Partner and Invoice/InvoiceLine persist to finance/accounting data.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from tera.core.database import Base


class Partner(Base):
    __tablename__ = "finance_partner"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    tax_id: Mapped[str | None] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    invoices: Mapped[list["Invoice"]] = relationship("Invoice", back_populates="partner")


class Product(Base):
    __tablename__ = "finance_product"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(16, 2), default=0, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Invoice(Base):
    __tablename__ = "finance_invoice"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    invoice_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    partner_id: Mapped[int] = mapped_column(ForeignKey("finance_partner.id"), nullable=False)
    
    date_invoice: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    
    amount_untaxed: Mapped[float] = mapped_column(Numeric(16, 2), default=0, nullable=False)
    amount_tax: Mapped[float] = mapped_column(Numeric(16, 2), default=0, nullable=False)
    amount_total: Mapped[float] = mapped_column(Numeric(16, 2), default=0, nullable=False)
    
    state: Mapped[str] = mapped_column(String(50), default="draft", nullable=False, index=True)
    
    notes: Mapped[str | None] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    partner: Mapped["Partner"] = relationship("Partner", back_populates="invoices")
    lines: Mapped[list["InvoiceLine"]] = relationship("InvoiceLine", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceLine(Base):
    __tablename__ = "finance_invoice_line"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("finance_invoice.id"), nullable=False)
    
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), default=1, nullable=False)
    price_unit: Mapped[float] = mapped_column(Numeric(16, 2), default=0, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(16, 2), default=0, nullable=False)

    # Relationships
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="lines")
