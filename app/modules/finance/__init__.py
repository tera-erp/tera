"""Finance module initialization."""
from app.core.database import AsyncSessionLocal
from app.modules.core import ActionRegistry, ActionContext, ActionResult


def _require_id(context: ActionContext) -> int:
    value = context.data.get("id")
    if value is None:
        raise ValueError("Invoice id is required")
    return int(value)


def _as_action_result(result) -> ActionResult:
    return ActionResult(success=result.success, message=result.message, data={"status": result.status})


async def submit_invoice(context: ActionContext) -> ActionResult:
    """Submit invoice for approval."""
    try:
        invoice_id = _require_id(context)
        from .router import _update_status

        async with AsyncSessionLocal() as db:
            result = await _update_status(invoice_id, "submitted", "Invoice submitted for approval", db)
        return _as_action_result(result)
    except Exception as exc:
        return ActionResult(success=False, message=f"Failed to submit invoice: {str(exc)}")


async def approve_invoice(context: ActionContext) -> ActionResult:
    """Approve invoice."""
    try:
        invoice_id = _require_id(context)
        if "finance.approve_invoice" not in context.metadata.get("permissions", []):
            return ActionResult(success=False, message="You don't have permission to approve invoices")

        from .router import _update_status

        async with AsyncSessionLocal() as db:
            result = await _update_status(invoice_id, "approved", "Invoice approved", db)
        return _as_action_result(result)
    except Exception as exc:
        return ActionResult(success=False, message=f"Failed to approve invoice: {str(exc)}")


async def reject_invoice(context: ActionContext) -> ActionResult:
    """Reject invoice."""
    try:
        invoice_id = _require_id(context)
        from .router import _update_status

        async with AsyncSessionLocal() as db:
            result = await _update_status(invoice_id, "draft", "Invoice rejected", db)
        return _as_action_result(result)
    except Exception as exc:
        return ActionResult(success=False, message=f"Failed to reject invoice: {str(exc)}")


async def mark_paid(context: ActionContext) -> ActionResult:
    """Mark invoice as paid."""
    try:
        invoice_id = _require_id(context)
        from .router import _update_status

        async with AsyncSessionLocal() as db:
            result = await _update_status(invoice_id, "paid", "Invoice marked as paid", db)
        return _as_action_result(result)
    except Exception as exc:
        return ActionResult(success=False, message=f"Failed to mark invoice as paid: {str(exc)}")


async def cancel_invoice(context: ActionContext) -> ActionResult:
    """Cancel invoice."""
    try:
        invoice_id = _require_id(context)
        from .router import _update_status

        async with AsyncSessionLocal() as db:
            result = await _update_status(invoice_id, "cancelled", "Invoice cancelled", db)
        return _as_action_result(result)
    except Exception as exc:
        return ActionResult(success=False, message=f"Failed to cancel invoice: {str(exc)}")


# Register actions
finance_actions = {
    "submit_invoice": submit_invoice,
    "approve_invoice": approve_invoice,
    "reject_invoice": reject_invoice,
    "mark_paid": mark_paid,
    "cancel_invoice": cancel_invoice,
}


def register_actions():
    """Register finance module actions."""
    ActionRegistry.register_module_actions("finance", finance_actions)
