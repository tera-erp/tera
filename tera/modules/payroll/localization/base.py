"""
Base Payroll Localization

Defines the interface and common utilities for country-specific payroll implementations.
"""
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class PayrollResult:
    """Standard payroll calculation result."""
    gross_pay: float
    net_pay: float
    deductions: Dict[str, float]
    employer_contributions: Dict[str, float]
    currency: str
    breakdown: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def total_deductions(self) -> float:
        return sum(self.deductions.values())
    
    @property
    def total_employer_contributions(self) -> float:
        return sum(self.employer_contributions.values())


class BasePayrollLocalization(ABC):
    """Base class for country-specific payroll implementations."""
    
    country_code: str = ""
    currency: str = ""
    
    @abstractmethod
    def calculate_payroll(
        self,
        employee: Dict[str, Any],
        base_salary: Decimal,
        allowances: Optional[Dict[str, Decimal]] = None,
        worked_days: int = None,
        total_days: int = None,
        overtime_hours: Decimal = Decimal("0"),
        **kwargs
    ) -> PayrollResult:
        """Calculate payroll for an employee."""
        pass
    
    def validate_employee_data(self, employee: Dict[str, Any]) -> bool:
        """Validate employee data has required fields for this localization."""
        return True
    
    def get_required_fields(self) -> list[str]:
        """Return list of required employee fields for this localization."""
        return []
    
    def format_amount(self, amount: Decimal) -> str:
        """Format amount according to local standards."""
        return f"{self.currency} {amount:,.2f}"
