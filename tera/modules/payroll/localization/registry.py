"""Payroll module localization registry scoped to the payroll module.
Includes a default non-localized strategy for environments without country-specific rules.
"""
from typing import Protocol, Dict, Type, TypedDict
from decimal import Decimal


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
    _strategies: Dict[str, Type[PayrollStrategy]] = {}
    _default_key = "DEFAULT"

    @classmethod
    def register(cls, country_code: str):
        def decorator(strategy_class: Type[PayrollStrategy]):
            cls._strategies[country_code] = strategy_class
            return strategy_class
        return decorator

    @classmethod
    def get_strategy(cls, country_code: str | None) -> PayrollStrategy:
        key = (country_code or cls._default_key).upper()
        strategy = cls._strategies.get(key) or cls._strategies.get(cls._default_key)
        if not strategy:
            raise ValueError("No payroll localization strategies are registered")
        return strategy()


payroll_registry = PayrollRegistry()


@payroll_registry.register(PayrollRegistry._default_key)
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
