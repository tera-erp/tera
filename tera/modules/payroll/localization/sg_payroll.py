from decimal import Decimal
from .registry import payroll_registry, PayrollResult


@payroll_registry.register("SG")
class SingaporePayrollStrategy:
    """CPF-centric payroll rules (simplified)."""

    def calculate_salary(self, gross_pay: Decimal, employee_profile: dict) -> PayrollResult:
        age = employee_profile.get("age", 30)
        is_pr = employee_profile.get("is_pr", True)

        if age <= 55:
            cpf_rate_ee = Decimal("0.20")
            cpf_rate_er = Decimal("0.17")
        elif age <= 60:
            cpf_rate_ee = Decimal("0.13")
            cpf_rate_er = Decimal("0.13")
        else:
            cpf_rate_ee = Decimal("0.075")
            cpf_rate_er = Decimal("0.09")

        capped_gross = min(gross_pay, Decimal("6800.00"))

        cpf_ee = capped_gross * cpf_rate_ee
        cpf_er = capped_gross * cpf_rate_er

        sdl = min(gross_pay * Decimal("0.0025"), Decimal("11.25"))

        return {
            "gross_pay": gross_pay,
            "employee_deduction": cpf_ee,
            "employer_contribution": cpf_er + sdl,
            "net_pay": gross_pay - cpf_ee,
            "details": {
                "CPF (Employee)": cpf_ee,
                "CPF (Employer)": cpf_er,
                "SDL": sdl,
            },
        }
