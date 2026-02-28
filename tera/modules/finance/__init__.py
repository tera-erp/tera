"""Finance module initialization."""
from .invoice import (submit_invoice, approve_invoice, reject_invoice,
                      mark_paid, cancel_invoice)
from tera.modules.core import ActionRegistry
from . import setup

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
