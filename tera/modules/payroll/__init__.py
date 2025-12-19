"""Payroll module actions registration.
Keeps payroll-specific actions self-contained and only depends on core primitives.
"""
from tera.core.database import AsyncSessionLocal
from tera.modules.core import ActionRegistry, ActionContext, ActionResult
from tera.modules.payroll.localization import payroll_registry  # Ensure strategies are loaded


def _require_id(context: ActionContext, *, key: str, label: str) -> int:
    value = context.data.get(key) or context.data.get("id")
    if value is None:
        raise ValueError(f"{label} id is required")
    return int(value)


async def deactivate_employee(context: ActionContext) -> ActionResult:
    try:
        employee_id = _require_id(context, key="employee_id", label="Employee")
        from .router import set_employee_status

        async with AsyncSessionLocal() as db:
            employee = await set_employee_status(employee_id, "inactive", db)

        return ActionResult(success=True, message="Employee deactivated", data={"status": employee.employment_status.value})
    except Exception as exc:
        return ActionResult(success=False, message=str(exc))


async def reactivate_employee(context: ActionContext) -> ActionResult:
    try:
        employee_id = _require_id(context, key="employee_id", label="Employee")
        from .router import set_employee_status

        async with AsyncSessionLocal() as db:
            employee = await set_employee_status(employee_id, "active", db)

        return ActionResult(success=True, message="Employee reactivated", data={"status": employee.employment_status.value})
    except Exception as exc:
        return ActionResult(success=False, message=str(exc))


async def terminate_employee(context: ActionContext) -> ActionResult:
    try:
        employee_id = _require_id(context, key="employee_id", label="Employee")
        from .router import set_employee_status

        async with AsyncSessionLocal() as db:
            employee = await set_employee_status(employee_id, "terminated", db)

        return ActionResult(success=True, message="Employee terminated", data={"status": employee.employment_status.value})
    except Exception as exc:
        return ActionResult(success=False, message=str(exc))


async def process_payroll(context: ActionContext) -> ActionResult:
    try:
        run_id = _require_id(context, key="run_id", label="Payroll run")
        from .router import set_payroll_run_status

        run = set_payroll_run_status(run_id, "processing")
        return ActionResult(success=True, message="Payroll processing started", data={"status": run.status})
    except Exception as exc:
        return ActionResult(success=False, message=str(exc))


async def complete_payroll(context: ActionContext) -> ActionResult:
    try:
        run_id = _require_id(context, key="run_id", label="Payroll run")
        from .router import set_payroll_run_status

        run = set_payroll_run_status(run_id, "completed")
        return ActionResult(success=True, message="Payroll processing completed", data={"status": run.status})
    except Exception as exc:
        return ActionResult(success=False, message=str(exc))


async def release_payment(context: ActionContext) -> ActionResult:
    try:
        run_id = _require_id(context, key="run_id", label="Payroll run")
        from .router import set_payroll_run_status

        run = set_payroll_run_status(run_id, "paid")
        return ActionResult(success=True, message="Payment released to all employees", data={"status": run.status})
    except Exception as exc:
        return ActionResult(success=False, message=str(exc))


async def revert_payroll(context: ActionContext) -> ActionResult:
    try:
        run_id = _require_id(context, key="run_id", label="Payroll run")
        from .router import set_payroll_run_status

        run = set_payroll_run_status(run_id, "draft")
        return ActionResult(success=True, message="Payroll reverted to draft", data={"status": run.status})
    except Exception as exc:
        return ActionResult(success=False, message=str(exc))


payroll_actions = {
    "deactivate_employee": deactivate_employee,
    "reactivate_employee": reactivate_employee,
    "terminate_employee": terminate_employee,
    "process_payroll": process_payroll,
    "complete_payroll": complete_payroll,
    "release_payment": release_payment,
    "revert_payroll": revert_payroll,
}


def register_actions() -> None:
    """Register payroll actions with the shared registry."""
    ActionRegistry.register_module_actions("payroll", payroll_actions)
