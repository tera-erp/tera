"""Payroll module router (module-scoped, DB-backed).
Payroll runs and payslips persist to the database.
"""
from decimal import Decimal
from typing import Optional, List
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from tera.core.database import get_db
from tera.modules.employees.models import EmployeeProfile, EmploymentStatus, EmploymentType
from tera.modules.company.models import Company
from tera.modules.users.models import User
from tera.modules.payroll.models import PayrollRun as PayrollRunModel, Payslip as PayslipModel
from tera.modules.payroll.localization import payroll_registry
from tera.modules.core.document_engine import DocumentEngine, DocumentFormat
from tera.modules.finance.documents import PayslipDocumentHelper

router = APIRouter(prefix="", tags=["Payroll"], responses={404: {"description": "Not found"}})

# --- Employee Schemas ---
class EmployeeCreate(BaseModel):
    """Schema for creating an employee (simplified for UI Factory)."""
    company_id: int
    employee_number: Optional[str] = None
    first_name: str
    last_name: str
    email: EmailStr
    mobile_phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    department: str
    position: str
    hire_date: date
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    base_salary: Optional[float] = None
    salary_currency: str = "USD"
    bank_account_number: Optional[str] = None
    bank_account_holder: Optional[str] = None
    bank_name: Optional[str] = None
    notes: Optional[str] = None


class EmployeeUpdate(BaseModel):
    """Schema for updating an employee."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    employee_number: Optional[str] = None
    mobile_phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    department: Optional[str] = None
    position: Optional[str] = None
    hire_date: Optional[date] = None
    employment_type: Optional[EmploymentType] = None
    employment_status: Optional[EmploymentStatus] = None
    base_salary: Optional[float] = None
    salary_currency: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_account_holder: Optional[str] = None
    bank_name: Optional[str] = None
    termination_date: Optional[date] = None
    notes: Optional[str] = None


class EmployeeResponse(BaseModel):
    """Response schema for employee list/detail."""
    id: int
    employee_number: str
    first_name: str
    last_name: str
    name: str  # Computed full name for list display
    email: str
    department: str
    position: str
    status: str
    employment_type: str
    hire_date: Optional[str] = None
    base_salary: Optional[float] = None
    salary_currency: Optional[str] = None
    mobile_phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_account_holder: Optional[str] = None
    bank_name: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class EmployeeStatusChangeResponse(BaseModel):
    success: bool
    message: str
    status: str


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
    status: str
    employee_count: int
    total_gross: float
    run_date: str

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
    country_code: str = Field(..., description="Country code (ID, SG, MY)")
    gross_salary: float = Field(..., gt=0, description="Monthly gross salary")
    age: int = Field(..., ge=18, le=70, description="Employee age")
    is_resident: bool = Field(default=True, description="Residency status (for SG)")
    ptkp_status: Optional[str] = Field(default="TK0", description="Tax status for Indonesia (TK0, K0, K1, K2, K3)")


# --- Employee Helpers ---
def _to_employee_response(emp: EmployeeProfile, user: User) -> EmployeeResponse:
    """Convert EmployeeProfile + User to EmployeeResponse."""
    full_name = f"{user.first_name} {user.last_name}".strip() or user.email
    return EmployeeResponse(
        id=emp.id,
        employee_number=emp.employee_number,
        first_name=user.first_name or "",
        last_name=user.last_name or "",
        name=full_name,
        email=user.email,
        department=emp.department or "",
        position=emp.position or "",
        status=emp.employment_status.value,
        employment_type=emp.employment_type.value,
        hire_date=emp.hire_date.isoformat() if emp.hire_date else None,
        base_salary=float(emp.base_salary) if emp.base_salary else None,
        salary_currency=emp.salary_currency,
        mobile_phone=emp.mobile_phone,
        date_of_birth=emp.date_of_birth.isoformat() if emp.date_of_birth else None,
        bank_account_number=emp.bank_account_number,
        bank_account_holder=emp.bank_account_holder,
        bank_name=emp.bank_name,
        notes=emp.notes,
    )


async def _get_employee(emp_id: int, db: AsyncSession) -> tuple[EmployeeProfile, User]:
    """Get employee profile with user."""
    result = await db.execute(
        select(EmployeeProfile)
        .options(joinedload(EmployeeProfile.user))
        .where(EmployeeProfile.id == emp_id)
    )
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee, employee.user


# --- Employee Routes ---
@router.get("/employees/", response_model=List[EmployeeResponse])
async def list_employees(db: AsyncSession = Depends(get_db)) -> List[EmployeeResponse]:
    """List all employees."""
    result = await db.execute(
        select(EmployeeProfile).options(joinedload(EmployeeProfile.user))
    )
    employees = result.scalars().unique().all()
    return [_to_employee_response(emp, emp.user) for emp in employees]


@router.get("/employees/{employee_id}/", response_model=EmployeeResponse)
async def get_employee(employee_id: int, db: AsyncSession = Depends(get_db)) -> EmployeeResponse:
    """Get employee detail."""
    employee, user = await _get_employee(employee_id, db)
    return _to_employee_response(employee, user)


@router.post("/employees/", response_model=EmployeeResponse, status_code=201)
async def create_employee(employee_data: EmployeeCreate, db: AsyncSession = Depends(get_db)) -> EmployeeResponse:
    """Create a new employee with an associated user account."""
    # Check if company exists
    result = await db.execute(select(Company).where(Company.id == employee_data.company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Check if email already exists
    result = await db.execute(select(User).where(User.email == employee_data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    # Generate employee number if not provided
    employee_number = employee_data.employee_number
    if not employee_number:
        result = await db.execute(
            select(EmployeeProfile)
            .where(EmployeeProfile.company_id == employee_data.company_id)
            .order_by(EmployeeProfile.id.desc())
        )
        last_emp = result.scalar_one_or_none()
        next_number = (last_emp.id + 1) if last_emp else 1
        employee_number = f"EMP-{next_number:05d}"

    # Check if employee number is unique within company
    result = await db.execute(
        select(EmployeeProfile).where(
            EmployeeProfile.company_id == employee_data.company_id,
            EmployeeProfile.employee_number == employee_number
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Employee number {employee_number} already exists")

    # Create user account
    # Generate username from email
    username = employee_data.email.split('@')[0]

    user = User(
        email=employee_data.email,
        username=username,
        first_name=employee_data.first_name,
        last_name=employee_data.last_name,
        company_id=employee_data.company_id,
        hashed_password="temporary_hash_to_be_reset",  #! Should be reset on first login
        is_verified=False,
    )
    db.add(user)
    await db.flush()

    # Create employee profile
    employee = EmployeeProfile(
        user_id=user.id,
        company_id=employee_data.company_id,
        employee_number=employee_number,
        mobile_phone=employee_data.mobile_phone,
        date_of_birth=employee_data.date_of_birth,
        department=employee_data.department,
        position=employee_data.position,
        job_title=employee_data.position,
        hire_date=employee_data.hire_date,
        employment_type=employee_data.employment_type,
        employment_status=EmploymentStatus.ACTIVE,
        base_salary=employee_data.base_salary,
        salary_currency=employee_data.salary_currency,
        bank_account_number=employee_data.bank_account_number,
        bank_account_holder=employee_data.bank_account_holder,
        bank_name=employee_data.bank_name,
        notes=employee_data.notes,
    )
    db.add(employee)
    await db.commit()
    await db.refresh(employee)
    await db.refresh(user)

    return _to_employee_response(employee, user)


@router.put("/employees/{employee_id}/", response_model=EmployeeResponse)
async def update_employee(employee_id: int, employee_data: EmployeeUpdate, db: AsyncSession = Depends(get_db)) -> EmployeeResponse:
    """Update an existing employee."""
    employee, user = await _get_employee(employee_id, db)

    # Update user fields (first_name, last_name)
    if employee_data.first_name is not None:
        user.first_name = employee_data.first_name
    if employee_data.last_name is not None:
        user.last_name = employee_data.last_name

    # Update employee profile fields
    if employee_data.employee_number is not None:
        # Check uniqueness if changing employee number
        if employee_data.employee_number != employee.employee_number:
            result = await db.execute(
                select(EmployeeProfile).where(
                    EmployeeProfile.company_id == employee.company_id,
                    EmployeeProfile.employee_number == employee_data.employee_number,
                    EmployeeProfile.id != employee_id
                )
            )
            if result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Employee number already exists")
        employee.employee_number = employee_data.employee_number

    if employee_data.mobile_phone is not None:
        employee.mobile_phone = employee_data.mobile_phone
    if employee_data.date_of_birth is not None:
        employee.date_of_birth = employee_data.date_of_birth
    if employee_data.department is not None:
        employee.department = employee_data.department
    if employee_data.position is not None:
        employee.position = employee_data.position
        employee.job_title = employee_data.position
    if employee_data.hire_date is not None:
        employee.hire_date = employee_data.hire_date
    if employee_data.employment_type is not None:
        employee.employment_type = employee_data.employment_type
    if employee_data.employment_status is not None:
        employee.employment_status = employee_data.employment_status
    if employee_data.base_salary is not None:
        employee.base_salary = employee_data.base_salary
    if employee_data.salary_currency is not None:
        employee.salary_currency = employee_data.salary_currency
    if employee_data.bank_account_number is not None:
        employee.bank_account_number = employee_data.bank_account_number
    if employee_data.bank_account_holder is not None:
        employee.bank_account_holder = employee_data.bank_account_holder
    if employee_data.bank_name is not None:
        employee.bank_name = employee_data.bank_name
    if employee_data.termination_date is not None:
        employee.termination_date = employee_data.termination_date
    if employee_data.notes is not None:
        employee.notes = employee_data.notes

    await db.commit()
    await db.refresh(employee)
    await db.refresh(user)

    return _to_employee_response(employee, user)


# --- Payroll Run Helpers ---
_STATUS_MAP = {
    "active": EmploymentStatus.ACTIVE,
    "inactive": EmploymentStatus.ON_LEAVE,
    "terminated": EmploymentStatus.TERMINATED,
}


def map_status(label: str) -> EmploymentStatus:
    try:
        return _STATUS_MAP[label]
    except KeyError as exc:
        raise ValueError(f"Unsupported status '{label}'") from exc


async def set_employee_status(employee_id: int, status_label: str, db: AsyncSession) -> EmployeeProfile:
    status_enum = map_status(status_label)
    result = await db.execute(select(EmployeeProfile).where(EmployeeProfile.id == employee_id))
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    employee.employment_status = status_enum
    await db.commit()
    await db.refresh(employee)
    return employee


async def get_payroll_run(run_id: int, db: AsyncSession) -> PayrollRunModel:
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
    run = await get_payroll_run(run_id, db)
    run.state = status
    await db.commit()
    await db.refresh(run)
    return PayrollRunActionResponse(success=True, message=message, status=run.state)


async def get_payslip(payslip_id: int, db: AsyncSession) -> PayslipModel:
    result = await db.execute(
        select(PayslipModel).where(PayslipModel.id == payslip_id)
    )
    payslip = result.scalar_one_or_none()
    if not payslip:
        raise HTTPException(status_code=404, detail="Payslip not found")
    return payslip



# --- Routes aligned with config.yaml ---
@router.get("/payroll-runs/", response_model=list[PayrollRunResponse])
async def list_payroll_runs(db: AsyncSession = Depends(get_db)) -> list[PayrollRunResponse]:
    result = await db.execute(select(PayrollRunModel).options(joinedload(PayrollRunModel.payslips)))
    runs = result.scalars().unique().all()
    return runs


@router.get("/payroll-runs/{run_id}/", response_model=PayrollRunResponse)
async def get_payroll_run_detail(run_id: int, db: AsyncSession = Depends(get_db)) -> PayrollRunResponse:
    run = await get_payroll_run(run_id, db)
    return run


@router.post("/payroll-runs/", response_model=PayrollRunResponse, status_code=201)
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


@router.put("/payroll-runs/{run_id}/", response_model=PayrollRunResponse)
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


@router.post("/payroll-runs/{run_id}/process", response_model=PayrollRunActionResponse)
async def process_payroll_run(run_id: int, db: AsyncSession = Depends(get_db)) -> PayrollRunActionResponse:
    return await update_payroll_run_status(run_id, "processing", "Payroll processing started", db)


@router.post("/payroll-runs/{run_id}/complete", response_model=PayrollRunActionResponse)
async def complete_payroll_run(run_id: int, db: AsyncSession = Depends(get_db)) -> PayrollRunActionResponse:
    return await update_payroll_run_status(run_id, "completed", "Payroll processing completed", db)


@router.post("/payroll-runs/{run_id}/release", response_model=PayrollRunActionResponse)
async def release_payroll_payment(run_id: int, db: AsyncSession = Depends(get_db)) -> PayrollRunActionResponse:
    return await update_payroll_run_status(run_id, "paid", "Payment released to all employees", db)


@router.post("/payroll-runs/{run_id}/revert", response_model=PayrollRunActionResponse)
async def revert_payroll_run(run_id: int, db: AsyncSession = Depends(get_db)) -> PayrollRunActionResponse:
    return await update_payroll_run_status(run_id, "draft", "Payroll reverted to draft", db)


@router.get("/payslips/{payslip_id}", response_model=PayslipResponse)
async def get_payslip_detail(payslip_id: int, db: AsyncSession = Depends(get_db)) -> PayslipResponse:
    payslip = await get_payslip(payslip_id, db)
    return payslip


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
    doc_data = PayslipDocumentHelper.prepare_document_data(
        payslip_id=payslip.id,
        payslip_number=payslip.payslip_number,
        employee_name=f"{employee_user.first_name} {employee_user.last_name}".strip() if employee_user else "Unknown",
        employee_id=str(payslip.employee_id),
        employee_email=employee_user.email if employee_user else None,
        employee_phone=employee.mobile_phone if employee else None,
        payroll_date=payslip.period_end or datetime.utcnow(),
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

    # Return direct Response since content is generated in-memory
    return Response(
        content=content if isinstance(content, (bytes, bytearray)) else content.encode("utf-8"),
        media_type=media_types[doc_format],
        headers={"Content-Disposition": f"attachment; filename=payslip_{payslip.payslip_number}.{doc_format.value}"},
    )


@router.get("/employees/{employee_id}/payslips", response_model=list[PayslipResponse])
async def list_employee_payslips(employee_id: int, db: AsyncSession = Depends(get_db)) -> list[PayslipResponse]:
    result = await db.execute(
        select(PayslipModel).where(PayslipModel.employee_id == employee_id)
    )
    payslips = result.scalars().all()
    if not payslips:
        raise HTTPException(status_code=404, detail="Payslips not found for employee")
    return payslips


@router.post("/employees/{employee_id}/deactivate", response_model=EmployeeStatusChangeResponse)
async def deactivate_employee(employee_id: int, db: AsyncSession = Depends(get_db)) -> EmployeeStatusChangeResponse:
    employee = await set_employee_status(employee_id, "inactive", db)
    return EmployeeStatusChangeResponse(success=True, message="Employee deactivated", status=employee.employment_status.value)


@router.post("/employees/{employee_id}/reactivate", response_model=EmployeeStatusChangeResponse)
async def reactivate_employee(employee_id: int, db: AsyncSession = Depends(get_db)) -> EmployeeStatusChangeResponse:
    employee = await set_employee_status(employee_id, "active", db)
    return EmployeeStatusChangeResponse(success=True, message="Employee reactivated", status=employee.employment_status.value)


@router.post("/employees/{employee_id}/terminate", response_model=EmployeeStatusChangeResponse)
async def terminate_employee(employee_id: int, db: AsyncSession = Depends(get_db)) -> EmployeeStatusChangeResponse:
    employee = await set_employee_status(employee_id, "terminated", db)
    return EmployeeStatusChangeResponse(success=True, message="Employee terminated", status=employee.employment_status.value)


@router.post("/payroll/calculate-preview")
async def calculate_payslip(data: PayslipPreviewRequest):
    """Calculate payroll deductions based on localization strategy."""
    try:
        strategy = payroll_registry.get_strategy(data.country_code)

        employee_profile = {
            "age": data.age,
            "is_pr": data.is_resident,
        }

        if data.country_code == "ID" and data.ptkp_status:
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

