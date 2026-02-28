"""Payroll localization - uses global localization registry.

This module registers payroll-specific handlers for different countries.
Maintains backward compatibility with existing payroll_registry usage.
"""
from .registry import payroll_registry, PayrollResult  # noqa: F401

# Register localization strategies
from . import id_payroll  # noqa: F401
from . import sg_payroll  # noqa: F401
from . import my_payroll  # noqa: F401

# Export for convenience
from tera.core.localization import localization_registry  # noqa: F401
