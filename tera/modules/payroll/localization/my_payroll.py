from decimal import Decimal
from .registry import payroll_registry, PayrollResult


@payroll_registry.register("MY")
class MalaysiaPayrollStrategy:
    """KWSP (EPF) and PERKESO (SOCSO) rules (simplified)."""

    def calculate_salary(self, gross_pay: Decimal, employee_profile: dict) -> PayrollResult:
        epf_rate_ee = Decimal("0.11")
        epf_rate_er = Decimal("0.13")

        epf_ee = gross_pay * epf_rate_ee
        epf_er = gross_pay * epf_rate_er

        socso_rate = Decimal("0.005")
        socso_deduction = min(gross_pay * socso_rate, Decimal("19.75"))

        eis_deduction = gross_pay * Decimal("0.002")

        total_deduction = epf_ee + socso_deduction + eis_deduction

        return {
            "gross_pay": gross_pay,
            "employee_deduction": total_deduction,
            "employer_contribution": epf_er + socso_deduction + eis_deduction,
            "net_pay": gross_pay - total_deduction,
            "details": {
                "EPF (Employee)": epf_ee,
                "SOCSO": socso_deduction,
                "EIS": eis_deduction,
            },
        }
