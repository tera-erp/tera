"""Payroll module router.
Payroll runs and payslips persist to the database.

This module focuses solely on payroll processing operations.
Employee management is handled by the employees module.
"""
from decimal import Decimal
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from tera.core.database import get_db
from tera.modules.employees.models import EmployeeProfile
from tera.modules.employees import EmployeeService
from tera.modules.company.models import Company
from tera.modules.payroll.models import PayrollRun as PayrollRunModel, Payslip as PayslipModel
from tera.modules.payroll.localization import payroll_registry
from tera.modules.core.document_engine import DocumentEngine, DocumentFormat
from tera.modules.finance.documents import PayslipDocumentHelper

router = APIRouter(prefix="", tags=["payroll"], responses={404: {"description": "Not found"}})


# --- Payroll Schemas ---
class PayrollRunCreate(BaseModel):
    """Schema for creating a payroll run."""
    company_id: int
    period_name: str
    employee_count: int = 0
    total_gross: float = 0.0
    total_deductions: float = 0.0
    total_net: float = 0.0
    run_date: Optional[datetime] = None
    notes: Optional[str] = None


class PayrollRunUpdate(BaseModel):
    """Schema for updating a payroll run."""
    period_name: Optional[str] = None
    employee_count: Optional[int] = None
    total_gross: Optional[float] = None
    total_deductions: Optional[float] = None
    total_net: Optional[float] = None
    run_date: Optional[datetime] = None
    notes: Optional[str] = None


class PayrollRunResponse(BaseModel):
    id: int
    period_name: str
    state: str
    employee_count: int
    total_gross: float
    total_net: float
    run_date: datetime

    class Config:
        from_attributes = True


class PayrollRunActionResponse(BaseModel):
    success: bool
    message: str
    status: str


class PayslipResponse(BaseModel):
    id: int
    employee_id: int
    period_name: str
    gross_salary: float
    total_deductions: float
    net_salary: float
    payment_status: str

    class Config:
        from_attributes = True


class PayslipPreviewRequest(BaseModel):
    country_code: str = Field(..., description="Country code (IDN, SGP, MYS)")
    gross_salary: float = Field(..., gt=0, description="Monthly gross salary")
    age: int = Field(..., ge=18, le=70, description="Employee age")
    is_resident: bool = Field(default=True, description="Residency status (for SGP)")
    ptkp_status: Optional[str] = Field(default="TK0", description="Tax status for Indonesia (TK0, K0, K1, K2, K3)")


# --- Helpers ---
async def get_payroll_run(run_id: int, db: AsyncSession) -> PayrollRunModel:
    """Get payroll run by ID."""
    result = await db.execute(
        select(PayrollRunModel)
        .options(joinedload(PayrollRunModel.payslips))
        .where(PayrollRunModel.id == run_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Payroll run not found")
    return run


async def update_payroll_run_status(run_id: int, status: str, message: str, db: AsyncSession) -> PayrollRunActionResponse:
    """Update payroll run status."""
    run = await get_payroll_run(run_id, db)
    run.state = status
    await db.commit()
    await db.refresh(run)
    return PayrollRunActionResponse(success=True, message=message, status=run.state)


async def get_payslip(payslip_id: int, db: AsyncSession) -> PayslipModel:
    """Get payslip by ID."""
    result = await db.execute(
        select(PayslipModel).where(PayslipModel.id == payslip_id)
    )
    payslip = result.scalar_one_or_none()
    if not payslip:
        raise HTTPException(status_code=404, detail="Payslip not found")
    return payslip


# --- Payroll Run Routes ---
@router.get("/runs/", response_model=list[PayrollRunResponse])
async def list_payroll_runs(db: AsyncSession = Depends(get_db)) -> list[PayrollRunResponse]:
    """List all payroll runs."""
    result = await db.execute(select(PayrollRunModel).options(joinedload(PayrollRunModel.payslips)))
    runs = result.scalars().unique().all()
    return runs


@router.get("/runs/{run_id}/", response_model=PayrollRunResponse)
async def get_payroll_run_detail(run_id: int, db: AsyncSession = Depends(get_db)) -> PayrollRunResponse:
    """Get payroll run detail."""
    run = await get_payroll_run(run_id, db)
    return run


@router.post("/runs/", response_model=PayrollRunResponse, status_code=201)
async def create_payroll_run(run_data: PayrollRunCreate, db: AsyncSession = Depends(get_db)) -> PayrollRunResponse:
    """Create a new payroll run."""
    # Verify company exists
    result = await db.execute(select(Company).where(Company.id == run_data.company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Create payroll run
    payroll_run = PayrollRunModel(
        company_id=run_data.company_id,
        period_name=run_data.period_name,
        employee_count=run_data.employee_count,
        total_gross=run_data.total_gross,
        total_deductions=run_data.total_deductions,
        total_net=run_data.total_net,
        run_date=run_data.run_date or datetime.utcnow(),
        notes=run_data.notes,
        state="draft",
    )
    db.add(payroll_run)
    await db.commit()
    await db.refresh(payroll_run)
    return payroll_run


@router.put("/runs/{run_id}/", response_model=PayrollRunResponse)
async def update_payroll_run(run_id: int, run_data: PayrollRunUpdate, db: AsyncSession = Depends(get_db)) -> PayrollRunResponse:
    """Update an existing payroll run."""
    run = await get_payroll_run(run_id, db)

    # Check if run is in editable state
    if run.state not in ("draft",):
        raise HTTPException(status_code=400, detail=f"Cannot edit payroll run in {run.state} state")

    # Update fields
    if run_data.period_name is not None:
        run.period_name = run_data.period_name
    if run_data.employee_count is not None:
        run.employee_count = run_data.employee_count
    if run_data.total_gross is not None:
        run.total_gross = run_data.total_gross
    if run_data.total_deductions is not None:
        run.total_deductions = run_data.total_deductions
    if run_data.total_net is not None:
        run.total_net = run_data.total_net
    if run_data.run_date is not None:
        run.run_date = run_data.run_date
    if run_data.notes is not None:
        run.notes = run_data.notes

    await db.commit()
    await db.refresh(run)
    return run


# --- Payroll Run Action Routes ---
@router.post("/runs/{run_id}/process", response_model=PayrollRunActionResponse)
async def process_payroll_run(run_id: int, db: AsyncSession = Depends(get_db)) -> PayrollRunActionResponse:
    """Start payroll processing."""
    return await update_payroll_run_status(run_id, "processing", "Payroll processing started", db)


@router.post("/runs/{run_id}/complete", response_model=PayrollRunActionResponse)
async def complete_payroll_run(run_id: int, db: AsyncSession = Depends(get_db)) -> PayrollRunActionResponse:
    """Complete payroll processing."""
    return await update_payroll_run_status(run_id, "completed", "Payroll processing completed", db)


@router.post("/runs/{run_id}/release", response_model=PayrollRunActionResponse)
async def release_payroll_payment(run_id: int, db: AsyncSession = Depends(get_db)) -> PayrollRunActionResponse:
    """Release payment to employees."""
    return await update_payroll_run_status(run_id, "paid", "Payment released to all employees", db)


@router.post("/runs/{run_id}/revert", response_model=PayrollRunActionResponse)
async def revert_payroll_run(run_id: int, db: AsyncSession = Depends(get_db)) -> PayrollRunActionResponse:
    """Revert payroll run to draft."""
    return await update_payroll_run_status(run_id, "draft", "Payroll reverted to draft", db)


# --- Payslip Routes ---
@router.get("/payslips/", response_model=list[PayslipResponse])
async def list_payslips(db: AsyncSession = Depends(get_db)) -> list[PayslipResponse]:
    """List all payslips."""
    result = await db.execute(select(PayslipModel))
    payslips = result.scalars().all()
    return payslips


@router.get("/payslips/{payslip_id}/", response_model=PayslipResponse)
async def get_payslip_detail(payslip_id: int, db: AsyncSession = Depends(get_db)) -> PayslipResponse:
    """Get payslip detail."""
    payslip = await get_payslip(payslip_id, db)
    return payslip


@router.get("/runs/{run_id}/payslips/", response_model=list[PayslipResponse])
async def list_payroll_run_payslips(run_id: int, db: AsyncSession = Depends(get_db)) -> list[PayslipResponse]:
    """List all payslips for a payroll run."""
    result = await db.execute(
        select(PayslipModel).where(PayslipModel.payroll_run_id == run_id)
    )
    payslips = result.scalars().all()
    return payslips


@router.get("/payslips/{payslip_id}/document")
async def generate_payslip_document(
    payslip_id: int,
    format: str = "pdf",
    db: AsyncSession = Depends(get_db),
):
    """Generate payslip document (pdf, html, json, xml)."""
    # Fetch payslip
    result = await db.execute(select(PayslipModel).where(PayslipModel.id == payslip_id))
    payslip = result.scalar_one_or_none()
    if not payslip:
        raise HTTPException(status_code=404, detail="Payslip not found")

    # Fetch employee (for name/contact)
    emp_result = await db.execute(
        select(EmployeeProfile)
        .options(joinedload(EmployeeProfile.user))
        .where(EmployeeProfile.id == payslip.employee_id)
    )
    employee = emp_result.scalar_one_or_none()
    employee_user = employee.user if employee else None

    # Validate format
    try:
        doc_format = DocumentFormat(format.lower())
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid format. Supported: pdf, html, json, xml") from e

    # Build salary/deduction components
    salary_components = [
        {"name": "Base Salary", "amount": float(payslip.base_salary or 0)},
    ]

    if payslip.allowances and isinstance(payslip.allowances, dict):
        for name, amount in payslip.allowances.items():
            salary_components.append({"name": name, "amount": float(amount or 0)})

    if payslip.overtime_amount:
        salary_components.append({"name": "Overtime", "amount": float(payslip.overtime_amount or 0)})

    deduction_components = []
    if payslip.deductions and isinstance(payslip.deductions, dict):
        for name, amount in payslip.deductions.items():
            deduction_components.append({"name": name, "amount": float(amount or 0)})

    # Prepare document data
    payroll_date = payslip.period_end
    if payroll_date and not isinstance(payroll_date, datetime):
        payroll_date = datetime.combine(payroll_date, datetime.min.time())
    payroll_date = payroll_date or datetime.utcnow()

    doc_data = PayslipDocumentHelper.prepare_document_data(
        payslip_id=payslip.id,
        payslip_number=payslip.payslip_number,
        employee_name=f"{employee_user.first_name} {employee_user.last_name}".strip() if employee_user else "Unknown",
        employee_id=str(payslip.employee_id),
        employee_email=employee_user.email if employee_user else None,
        employee_phone=employee.mobile_phone if employee else None,
        payroll_date=payroll_date,
        currency=employee.salary_currency if employee and getattr(employee, "salary_currency", None) else "USD",
        gross_salary=float(payslip.gross_salary or 0),
        deductions=float(payslip.total_deductions or 0),
        net_salary=float(payslip.net_salary or 0),
        salary_components=salary_components,
        deduction_components=deduction_components,
        notes=payslip.notes,
    )

    engine = DocumentEngine()
    content = engine.generate(doc_data, doc_format)

    media_types = {
        DocumentFormat.PDF: "application/pdf",
        DocumentFormat.HTML: "text/html",
        DocumentFormat.JSON: "application/json",
        DocumentFormat.XML: "application/xml",
    }

    return Response(
        content=content if isinstance(content, (bytes, bytearray)) else content.encode("utf-8"),
        media_type=media_types[doc_format],
        headers={"Content-Disposition": f"attachment; filename=payslip_{payslip.payslip_number}.{doc_format.value}"},
    )


# --- Payroll Calculator ---
@router.post("/calculate-preview")
async def calculate_payslip(data: PayslipPreviewRequest):
    """Calculate payroll deductions based on localization strategy."""
    try:
        strategy = payroll_registry.get_strategy(data.country_code)

        employee_profile = {
            "age": data.age,
            "is_pr": data.is_resident,
        }

        if data.country_code == "IDN" and data.ptkp_status:
            employee_profile["ptkp_status"] = data.ptkp_status

        gross = Decimal(str(data.gross_salary))
        result = strategy.calculate_salary(gross, employee_profile)

        return {
            "gross_pay": float(result["gross_pay"]),
            "employee_deduction": float(result["employee_deduction"]),
            "employer_contribution": float(result["employer_contribution"]),
            "net_pay": float(result["net_pay"]),
            "details": {k: float(v) for k, v in result["details"].items()},
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(exc)}")

