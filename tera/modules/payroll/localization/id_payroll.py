from decimal import Decimal
from .registry import payroll_registry, PayrollResult


@payroll_registry.register("ID")  # Maps to IDN internally
class IndonesiaPayrollStrategy:
    """Indonesian payroll deduction rules (BPJS, PPh 21)."""

    BPJS_HEALTH_RATE_EMPLOYEE = Decimal("0.01")
    BPJS_HEALTH_SALARY_CAP = Decimal("12000000")

    BPJS_JHT_RATE_EMPLOYEE = Decimal("0.02")
    BPJS_JP_RATE_EMPLOYEE = Decimal("0.01")
    BPJS_PENSION_SALARY_CAP = Decimal("10054900")

    OCCUPATIONAL_EXPENSE_RATE = Decimal("0.05")
    MAX_OCCUPATIONAL_EXPENSE_MONTHLY = Decimal("500000")

    PTKP_RATES = {
        "TK0": Decimal("54000000"),
        "K0": Decimal("58500000"),
        "K1": Decimal("63000000"),
        "K2": Decimal("67500000"),
        "K3": Decimal("72000000"),
    }

    TAX_BRACKETS = [
        (Decimal("60000000"), Decimal("0.05")),
        (Decimal("250000000"), Decimal("0.15")),
        (Decimal("500000000"), Decimal("0.25")),
        (Decimal("5000000000"), Decimal("0.30")),
        (Decimal("Infinity"), Decimal("0.35")),
    ]

    def calculate_deductions(self, gross_salary: Decimal, ptkp_status: str = "TK0") -> dict:
        deductions = {}

        health_base = min(gross_salary, self.BPJS_HEALTH_SALARY_CAP)
        deductions["bpjs_kesehatan"] = (health_base * self.BPJS_HEALTH_RATE_EMPLOYEE).quantize(Decimal("0"))

        deductions["bpjs_jht"] = (gross_salary * self.BPJS_JHT_RATE_EMPLOYEE).quantize(Decimal("0"))

        pension_base = min(gross_salary, self.BPJS_PENSION_SALARY_CAP)
        deductions["bpjs_jp"] = (pension_base * self.BPJS_JP_RATE_EMPLOYEE).quantize(Decimal("0"))

        deductions["pph_21"] = self._calculate_pph21(gross_salary, deductions, ptkp_status)
        return deductions

    def _calculate_pph21(self, gross_salary: Decimal, current_deductions: dict, ptkp_status: str) -> Decimal:
        occupational_expense = min(
            gross_salary * self.OCCUPATIONAL_EXPENSE_RATE,
            self.MAX_OCCUPATIONAL_EXPENSE_MONTHLY,
        )
        jht_deduction = current_deductions.get("bpjs_jht", Decimal(0))
        jp_deduction = current_deductions.get("bpjs_jp", Decimal(0))
        total_monthly_deductions = occupational_expense + jht_deduction + jp_deduction

        net_monthly_income = gross_salary - total_monthly_deductions
        net_annual_income = net_monthly_income * 12

        ptkp_amount = self.PTKP_RATES.get(ptkp_status.upper())
        if ptkp_amount is None:
            raise ValueError(f"Invalid PTKP status: {ptkp_status}")

        taxable_annual_income = net_annual_income - ptkp_amount
        if taxable_annual_income <= 0:
            return Decimal("0")

        annual_tax = Decimal("0")
        remaining_income = taxable_annual_income

        for i, (bracket_limit, rate) in enumerate(self.TAX_BRACKETS):
            previous_bracket_limit = self.TAX_BRACKETS[i - 1][0] if i > 0 else 0
            taxable_in_bracket = min(remaining_income, bracket_limit - previous_bracket_limit)
            annual_tax += taxable_in_bracket * rate
            remaining_income -= taxable_in_bracket
            if remaining_income <= 0:
                break

        monthly_tax = (annual_tax / 12).quantize(Decimal("0"))
        return monthly_tax

    def calculate_salary(self, gross_pay: Decimal, employee_profile: dict) -> PayrollResult:
        ptkp_status = employee_profile.get("ptkp_status", "TK0")

        deductions = self.calculate_deductions(gross_pay, ptkp_status)
        total_employee_deduction = (
            deductions["bpjs_kesehatan"]
            + deductions["bpjs_jht"]
            + deductions["bpjs_jp"]
            + deductions["pph_21"]
        )

        health_base = min(gross_pay, self.BPJS_HEALTH_SALARY_CAP)
        employer_health = (health_base * Decimal("0.04")).quantize(Decimal("0"))
        employer_jht = (gross_pay * Decimal("0.037")).quantize(Decimal("0"))
        pension_base = min(gross_pay, self.BPJS_PENSION_SALARY_CAP)
        employer_jp = (pension_base * Decimal("0.02")).quantize(Decimal("0"))
        employer_jkk = (gross_pay * Decimal("0.0054")).quantize(Decimal("0"))
        employer_jkm = (gross_pay * Decimal("0.003")).quantize(Decimal("0"))

        total_employer_contribution = (
            employer_health
            + employer_jht
            + employer_jp
            + employer_jkk
            + employer_jkm
        )

        net_pay = gross_pay - total_employee_deduction

        return {
            "gross_pay": gross_pay,
            "employee_deduction": total_employee_deduction,
            "employer_contribution": total_employer_contribution,
            "net_pay": net_pay,
            "details": {
                "BPJS Kesehatan (Employee)": deductions["bpjs_kesehatan"],
                "BPJS JHT (Employee)": deductions["bpjs_jht"],
                "BPJS JP (Employee)": deductions["bpjs_jp"],
                "PPh 21": deductions["pph_21"],
                "BPJS Kesehatan (Employer)": employer_health,
                "BPJS JHT (Employer)": employer_jht,
                "BPJS JP (Employer)": employer_jp,
                "BPJS JKK (Employer)": employer_jkk,
                "BPJS JKM (Employer)": employer_jkm,
            },
        }
