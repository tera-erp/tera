"""Payroll localization registry - migrated to use global localization system.

This maintains backward compatibility while delegating to the global registry.
"""
from typing import Protocol, Dict, Type, TypedDict
from decimal import Decimal
from tera.core.localization import localization_registry


class PayrollResult(TypedDict):
    gross_pay: Decimal
    employee_deduction: Decimal
    employer_contribution: Decimal
    net_pay: Decimal
    details: Dict[str, Decimal]


class PayrollStrategy(Protocol):
    def calculate_salary(self, gross_pay: Decimal, employee_profile: dict) -> PayrollResult:
        ...


class PayrollRegistry:
    """Legacy payroll registry - delegates to global localization registry."""
    _default_key = "DEFAULT"

    @classmethod
    def register(cls, country_code: str):
        """Decorator for registering payroll strategies.
        
        Now delegates to the global localization registry under 'payroll' domain.
        """
        # Map old 2-letter codes to 3-letter ISO codes if needed
        code_map = {
            "ID": "IDN",
            "MY": "MYS", 
            "SG": "SGP",
        }
        iso_code = code_map.get(country_code.upper(), country_code.upper())
        
        return localization_registry.register(iso_code, "payroll")

    @classmethod
    def get_strategy(cls, country_code: str | None) -> PayrollStrategy:
        """Get payroll strategy for a country.
        
        Args:
            country_code: 2 or 3 letter country code (ID/IDN, MY/MYS, SG/SGP)
        
        Returns:
            PayrollStrategy instance
        """
        if not country_code:
            country_code = cls._default_key
        
        # Map old 2-letter codes to 3-letter ISO codes
        code_map = {
            "ID": "IDN",
            "MY": "MYS",
            "SG": "SGP",
        }
        iso_code = code_map.get(country_code.upper(), country_code.upper())
        
        # Try to get from global registry
        handler = localization_registry.get(iso_code, "payroll")
        if handler:
            return handler
        
        # Fall back to default
        handler = localization_registry.get_or_raise(cls._default_key, "payroll")
        return handler


payroll_registry = PayrollRegistry()


# Register default handler
@localization_registry.register_default("payroll")
class DefaultPayrollStrategy:
    """Fallback when no localization is required."""

    def calculate_salary(self, gross_pay: Decimal, employee_profile: dict) -> PayrollResult:
        return {
            "gross_pay": gross_pay,
            "employee_deduction": Decimal("0"),
            "employer_contribution": Decimal("0"),
            "net_pay": gross_pay,
            "details": {},
        }
