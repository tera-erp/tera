"""Finance module router (module-scoped, DB-backed).
All endpoints align with finance/config.yaml and rely only on shared core services.
"""
from decimal import Decimal
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from fastapi.responses import FileResponse

from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.finance.models import Invoice as InvoiceModel, InvoiceLine as InvoiceLineModel, Partner as PartnerModel, Product as ProductModel
from app.modules.finance.documents import InvoiceDocumentHelper
from app.modules.core.document_engine import DocumentEngine, DocumentFormat

router = APIRouter(prefix="/invoices", tags=["Finance"], responses={404: {"description": "Not found"}})


# --- Models ---
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
    country_code: str = Field(..., min_length=2, max_length=2)
    email: Optional[str] = None
    phone: Optional[str] = None
    tax_id: Optional[str] = None
    address: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    country_code: Optional[str] = Field(default=None, min_length=2, max_length=2)
    email: Optional[str] = None
    phone: Optional[str] = None
    tax_id: Optional[str] = None
    address: Optional[str] = None


@router.get("/customers", response_model=List[CustomerResponse])
@router.get("/customers/", response_model=List[CustomerResponse])
async def list_customers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all customers (partners)."""
    query = select(PartnerModel).offset(skip).limit(limit)
    result = await db.execute(query)
    partners = result.scalars().all()
    return partners


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
@router.get("/customers/{customer_id}/", response_model=CustomerResponse)
async def get_customer(customer_id: int, db: AsyncSession = Depends(get_db)):
    partner = await db.get(PartnerModel, customer_id)
    if not partner:
        raise HTTPException(status_code=404, detail="Customer not found")
    return partner


@router.post("/customers", response_model=CustomerResponse, status_code=201)
@router.post("/customers/", response_model=CustomerResponse, status_code=201)
async def create_customer(customer: CustomerCreate, db: AsyncSession = Depends(get_db)):
    partner = PartnerModel(
        name=customer.name,
        country_code=customer.country_code.upper(),
        email=customer.email,
        phone=customer.phone,
        tax_id=customer.tax_id,
        address=customer.address,
    )
    db.add(partner)
    await db.commit()
    await db.refresh(partner)
    return partner


@router.put("/customers/{customer_id}", response_model=CustomerResponse)
@router.put("/customers/{customer_id}/", response_model=CustomerResponse)
async def update_customer(customer_id: int, customer: CustomerUpdate, db: AsyncSession = Depends(get_db)):
    partner = await db.get(PartnerModel, customer_id)
    if not partner:
        raise HTTPException(status_code=404, detail="Customer not found")

    for field, value in customer.model_dump(exclude_unset=True).items():
        if field == "country_code" and value:
            setattr(partner, field, value.upper())
        elif value is not None:
            setattr(partner, field, value)

    await db.commit()
    await db.refresh(partner)
    return partner


class ProductResponse(BaseModel):
    """Response for product list."""
    id: int
    name: str
    price: Decimal = Decimal(0)

    class Config:
        from_attributes = True


@router.get("/products", response_model=List[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all products."""
    query = select(ProductModel).offset(skip).limit(limit)
    result = await db.execute(query)
    products = result.scalars().all()
    return products


# --- Helpers ---
def _invoice_number(inv: InvoiceModel) -> str:
    # If a proper field is added later, replace this fallback
    return f"INV-{inv.id:05d}"


def _to_invoice(inv: InvoiceModel) -> Invoice:
    line_items = [
        InvoiceLine(
            product_name=line.product_name or "",
            qty=Decimal(line.quantity),
            unit_price=Decimal(line.price_unit),
            amount=Decimal(line.quantity) * Decimal(line.price_unit),
            description=line.description,
        )
        for line in inv.lines
    ]

    customer_name = inv.partner.name if inv.partner else ""
    total = Decimal(inv.amount_total) if inv.amount_total is not None else Decimal(0)
    return Invoice(
        id=inv.id,
        invoice_number=_invoice_number(inv),
        customer_name=customer_name,
        status=inv.state,
        total=total,
        invoice_date=inv.date_invoice.date().isoformat() if inv.date_invoice else "",
        line_items=line_items,
    )


async def _get_invoice(inv_id: int, db: AsyncSession) -> InvoiceModel:
    result = await db.execute(
        select(InvoiceModel)
        .options(joinedload(InvoiceModel.partner), joinedload(InvoiceModel.lines))
        .where(InvoiceModel.id == inv_id)
    )
    invoice = result.unique().scalar_one_or_none()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


async def _update_status(inv_id: int, status: str, message: str, db: AsyncSession) -> InvoiceActionResponse:
    invoice = await _get_invoice(inv_id, db)
    invoice.state = status
    await db.commit()
    await db.refresh(invoice)
    return InvoiceActionResponse(success=True, message=message, status=invoice.state)


# --- Routes aligned with config.yaml ---
@router.get("", response_model=List[Invoice])
@router.get("/", response_model=List[Invoice])
async def list_invoices(db: AsyncSession = Depends(get_db)) -> List[Invoice]:
    result = await db.execute(
        select(InvoiceModel).options(joinedload(InvoiceModel.partner), joinedload(InvoiceModel.lines))
    )
    invoices = result.scalars().unique().all()
    return [_to_invoice(inv) for inv in invoices]


@router.get("/{invoice_id}", response_model=Invoice)
@router.get("/{invoice_id}/", response_model=Invoice)
async def get_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)) -> Invoice:
    invoice = await _get_invoice(invoice_id, db)
    return _to_invoice(invoice)


@router.post("", response_model=Invoice, status_code=201)
@router.post("/", response_model=Invoice, status_code=201)
async def create_invoice(invoice_data: InvoiceCreate, db: AsyncSession = Depends(get_db)) -> Invoice:
    """Create a new invoice."""
    # Verify partner exists
    result = await db.execute(select(PartnerModel).where(PartnerModel.id == invoice_data.customer_id))
    partner = result.scalar_one_or_none()
    if not partner:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Generate invoice number (simple counter-based)
    result = await db.execute(
        select(InvoiceModel.id).order_by(InvoiceModel.id.desc()).limit(1)
    )
    last_id = result.scalars().first()
    next_number = (last_id + 1) if last_id is not None else 1
    invoice_number = f"INV-{next_number:05d}"

    # Create invoice
    invoice = InvoiceModel(
        invoice_number=invoice_number,
        partner_id=invoice_data.customer_id,
        date_invoice=invoice_data.invoice_date or datetime.utcnow(),
        currency_code=invoice_data.currency_code,
        amount_untaxed=float(invoice_data.amount_untaxed),
        amount_tax=float(invoice_data.amount_tax),
        amount_total=float(invoice_data.amount_total),
        notes=invoice_data.notes,
        state="draft",
    )
    db.add(invoice)
    await db.flush()

    # Add line items
    if invoice_data.line_items:
        for line_data in invoice_data.line_items:
            product_name = line_data.product_name
            if line_data.product_id and not product_name:
                product_result = await db.execute(select(ProductModel).where(ProductModel.id == line_data.product_id))
                product = product_result.scalar_one_or_none()
                if product:
                    product_name = product.name
            
            line = InvoiceLineModel(
                invoice_id=invoice.id,
                product_name=product_name or "Unknown Product",
                quantity=float(line_data.quantity),
                price_unit=float(line_data.price_unit),
                amount=float(line_data.quantity * line_data.price_unit),
                description=line_data.description,
            )
            db.add(line)

    await db.commit()
    await db.refresh(invoice)
    
    # Reload with relationships
    result = await db.execute(
        select(InvoiceModel)
        .options(joinedload(InvoiceModel.partner), joinedload(InvoiceModel.lines))
        .where(InvoiceModel.id == invoice.id)
    )
    invoice = result.unique().scalar_one()
    return _to_invoice(invoice)


@router.put("/{invoice_id}", response_model=Invoice)
@router.put("/{invoice_id}/", response_model=Invoice)
async def update_invoice(invoice_id: int, invoice_data: InvoiceUpdate, db: AsyncSession = Depends(get_db)) -> Invoice:
    """Update an existing invoice."""
    invoice = await _get_invoice(invoice_id, db)

    # Check if invoice is in editable state
    if invoice.state not in ("draft",):
        raise HTTPException(status_code=400, detail=f"Cannot edit invoice in {invoice.state} state")

    # Update fields
    if invoice_data.customer_id is not None:
        result = await db.execute(select(PartnerModel).where(PartnerModel.id == invoice_data.customer_id))
        partner = result.scalar_one_or_none()
        if not partner:
            raise HTTPException(status_code=404, detail="Customer not found")
        invoice.partner_id = invoice_data.customer_id

    if invoice_data.invoice_date is not None:
        invoice.date_invoice = invoice_data.invoice_date
    if invoice_data.currency_code is not None:
        invoice.currency_code = invoice_data.currency_code
    if invoice_data.amount_untaxed is not None:
        invoice.amount_untaxed = float(invoice_data.amount_untaxed)
    if invoice_data.amount_tax is not None:
        invoice.amount_tax = float(invoice_data.amount_tax)
    if invoice_data.amount_total is not None:
        invoice.amount_total = float(invoice_data.amount_total)
    if invoice_data.notes is not None:
        invoice.notes = invoice_data.notes

    # Update line items if provided
    if invoice_data.line_items is not None:
        # Delete existing lines
        for line in invoice.lines:
            await db.delete(line)
        
        # Add new lines
        for line_data in invoice_data.line_items:
            product_name = line_data.product_name
            if line_data.product_id and not product_name:
                product_result = await db.execute(select(ProductModel).where(ProductModel.id == line_data.product_id))
                product = product_result.scalar_one_or_none()
                if product:
                    product_name = product.name

            line = InvoiceLineModel(
                invoice_id=invoice.id,
                product_name=product_name or "",
                quantity=float(line_data.quantity or 1),
                price_unit=float(line_data.price_unit or 0),
                amount=float((line_data.quantity or 1) * (line_data.price_unit or 0)),
                description=line_data.description,
            )
            db.add(line)

    await db.commit()
    await db.refresh(invoice)
    
    # Reload with relationships
    result = await db.execute(
        select(InvoiceModel)
        .options(joinedload(InvoiceModel.partner), joinedload(InvoiceModel.lines))
        .where(InvoiceModel.id == invoice.id)
    )
    invoice = result.unique().scalar_one()
    return _to_invoice(invoice)



@router.post("/{invoice_id}/submit", response_model=InvoiceActionResponse)
async def submit_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)) -> InvoiceActionResponse:
    return await _update_status(invoice_id, "submitted", "Invoice submitted for approval", db)


@router.post("/{invoice_id}/approve", response_model=InvoiceActionResponse)
async def approve_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)) -> InvoiceActionResponse:
    return await _update_status(invoice_id, "approved", "Invoice approved", db)


@router.post("/{invoice_id}/reject", response_model=InvoiceActionResponse)
async def reject_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)) -> InvoiceActionResponse:
    return await _update_status(invoice_id, "draft", "Invoice rejected", db)


@router.post("/{invoice_id}/mark-paid", response_model=InvoiceActionResponse)
async def mark_paid(invoice_id: int, db: AsyncSession = Depends(get_db)) -> InvoiceActionResponse:
    return await _update_status(invoice_id, "paid", "Invoice marked as paid", db)


@router.post("/{invoice_id}/cancel", response_model=InvoiceActionResponse)
async def cancel_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)) -> InvoiceActionResponse:
    return await _update_status(invoice_id, "cancelled", "Invoice cancelled", db)


@router.get("/{invoice_id}/document")
async def generate_document(
    invoice_id: int,
    format: str = "pdf",
    db: AsyncSession = Depends(get_db),
):
    """Generate invoice document in specified format (pdf, html, json, xml)."""
    # Fetch invoice with relationships
    result = await db.execute(
        select(InvoiceModel)
        .options(joinedload(InvoiceModel.partner), joinedload(InvoiceModel.lines))
        .where(InvoiceModel.id == invoice_id)
    )
    invoice = result.scalar_one_or_none()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Validate format
    try:
        doc_format = DocumentFormat(format.lower())
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid format. Supported: pdf, html, json, xml") from e
    
    # Prepare line items data
    line_items_data = [
        {
            "product_name": line.product_name,
            "quantity": float(line.quantity),
            "price_unit": float(line.price_unit),
            "amount": float(line.amount or 0),
        }
        for line in invoice.lines
    ]
    
    # Use helper to prepare document data
    doc_data = InvoiceDocumentHelper.prepare_document_data(
        invoice_id=invoice.id,
        invoice_number=_invoice_number(invoice),
        customer_name=invoice.partner.name if invoice.partner else "Unknown",
        customer_email=invoice.partner.email if invoice.partner else None,
        customer_phone=invoice.partner.phone if invoice.partner else None,
        customer_country=invoice.partner.country_code if invoice.partner else None,
        invoice_date=invoice.date_invoice or datetime.now(),
        currency=invoice.currency_code or "USD",
        amount_untaxed=float(invoice.amount_untaxed or 0),
        amount_tax=float(invoice.amount_tax or 0),
        amount_total=float(invoice.amount_total or 0),
        line_items=line_items_data,
        notes=invoice.notes,
    )
    
    # Generate document
    engine = DocumentEngine()
    content = engine.generate(doc_data, doc_format)
    
    # Return appropriate response type
    if doc_format == DocumentFormat.PDF:
        return FileResponse(
            content=content,
            media_type="application/pdf",
            filename=f"invoice_{_invoice_number(invoice)}.pdf",
        )
    elif doc_format == DocumentFormat.HTML:
        return FileResponse(
            content=content.encode("utf-8") if isinstance(content, str) else content,
            media_type="text/html",
            filename=f"invoice_{_invoice_number(invoice)}.html",
        )
    elif doc_format == DocumentFormat.JSON:
        return FileResponse(
            content=content.encode("utf-8") if isinstance(content, str) else content,
            media_type="application/json",
            filename=f"invoice_{_invoice_number(invoice)}.json",
        )
    else:  # XML
        return FileResponse(
            content=content.encode("utf-8") if isinstance(content, str) else content,
            media_type="application/xml",
            filename=f"invoice_{_invoice_number(invoice)}.xml",
        )
