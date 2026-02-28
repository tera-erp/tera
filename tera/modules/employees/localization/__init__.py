"""Employee localization registry and handlers.

This module provides country-specific employee data requirements and validation.
"""
from tera.core.localization import localization_registry


@localization_registry.register_default("employees")
class DefaultEmployeeHandler:
    """Default employee handler with minimal requirements."""
    
    def get_required_fields(self) -> list[str]:
        """Basic fields required for all employees."""
        return [
            "first_name",
            "last_name", 
            "email",
            "hire_date",
        ]
    
    def get_optional_fields(self) -> list[str]:
        """Optional fields available for all employees."""
        return [
            "middle_name",
            "phone",
            "address",
            "emergency_contact",
            "bank_account",
        ]
    
    def validate_data(self, employee_data: dict) -> tuple[bool, list[str]]:
        """Validate employee data."""
        errors = []
        
        for field in self.get_required_fields():
            if not employee_data.get(field):
                errors.append(f"Required field '{field}' is missing")
        
        return (len(errors) == 0, errors)
    
    def get_tax_id_name(self) -> str:
        """Generic tax ID name."""
        return "Tax ID"
    
    def get_localization_schema(self) -> dict:
        """Get JSON schema for localization_data field."""
        return {}


@localization_registry.register("IDN", "employees")
class IndonesiaEmployeeHandler:
    """Indonesian employee-specific requirements."""
    
    def get_required_fields(self) -> list[str]:
        """Required fields for Indonesian employees."""
        return [
            "first_name",
            "last_name",
            "email",
            "hire_date",
            "tax_id",  # NPWP
            "nationality",
            "country",
        ]
    
    def get_optional_fields(self) -> list[str]:
        """Optional Indonesia-specific fields."""
        return [
            "ptkp_status",  # Tax status
            "bpjs_kesehatan_number",  # Health insurance
            "bpjs_ketenagakerjaan_number",  # Employment insurance
            "ktp_number",  # National ID
            "kk_number",  # Family card
            "religion",  # Required on some official docs
        ]
    
    def validate_data(self, employee_data: dict) -> tuple[bool, list[str]]:
        """Validate Indonesian employee data."""
        errors = []
        
        # Check required fields
        for field in self.get_required_fields():
            if not employee_data.get(field):
                errors.append(f"Required field '{field}' is missing")
        
        # Validate NPWP format (basic check: 15 digits)
        tax_id = employee_data.get("tax_id", "")
        if tax_id and not self._validate_npwp(tax_id):
            errors.append("NPWP must be 15 digits (format: XX.XXX.XXX.X-XXX.XXX)")
        
        # Validate PTKP status if provided
        ptkp = employee_data.get("ptkp_status")
        if ptkp and ptkp not in ["TK0", "TK1", "TK2", "TK3", "K0", "K1", "K2", "K3"]:
            errors.append(f"Invalid PTKP status: {ptkp}")
        
        return (len(errors) == 0, errors)
    
    def get_tax_id_name(self) -> str:
        """Indonesian tax ID name."""
        return "NPWP (Nomor Pokok Wajib Pajak)"
    
    def get_localization_schema(self) -> dict:
        """JSON schema for Indonesian employee data."""
        return {
            "type": "object",
            "properties": {
                "ptkp_status": {
                    "type": "string",
                    "enum": ["TK0", "TK1", "TK2", "TK3", "K0", "K1", "K2", "K3"],
                    "description": "Penghasilan Tidak Kena Pajak status"
                },
                "bpjs_kesehatan_number": {
                    "type": "string",
                    "description": "BPJS Kesehatan (Health) number"
                },
                "bpjs_ketenagakerjaan_number": {
                    "type": "string",
                    "description": "BPJS Ketenagakerjaan (Employment) number"
                },
                "ktp_number": {
                    "type": "string",
                    "pattern": "^[0-9]{16}$",
                    "description": "KTP (National ID) 16 digits"
                },
                "kk_number": {
                    "type": "string",
                    "pattern": "^[0-9]{16}$",
                    "description": "Kartu Keluarga (Family Card) 16 digits"
                },
                "religion": {
                    "type": "string",
                    "enum": ["Islam", "Kristen", "Katolik", "Hindu", "Buddha", "Konghucu"],
                    "description": "Religion (required on KTP)"
                }
            }
        }
    
    def _validate_npwp(self, npwp: str) -> bool:
        """Validate NPWP format."""
        # Remove formatting characters
        digits = ''.join(c for c in npwp if c.isdigit())
        return len(digits) == 15
    
    def get_statutory_requirements(self) -> dict:
        """Get Indonesian employment law requirements."""
        return {
            "minimum_wage_regions": ["DKI Jakarta", "West Java", "East Java"],
            "probation_period_max_days": 90,
            "annual_leave_min_days": 12,
            "notice_period_days": 30,
            "severance_formula": "Based on tenure and salary",
        }


@localization_registry.register("MYS", "employees")
class MalaysiaEmployeeHandler:
    """Malaysian employee-specific requirements."""
    
    def get_required_fields(self) -> list[str]:
        """Required fields for Malaysian employees."""
        return [
            "first_name",
            "last_name",
            "email",
            "hire_date",
            "tax_id",  # Income Tax Number
            "nationality",
            "country",
        ]
    
    def get_optional_fields(self) -> list[str]:
        """Optional Malaysia-specific fields."""
        return [
            "ic_number",  # MyKad/IC number
            "epf_number",  # EPF (Pension fund)
            "socso_number",  # SOCSO (Social security)
            "eis_number",  # EIS (Employment insurance)
            "passport_number",
            "race",  # Common on Malaysian forms
        ]
    
    def validate_data(self, employee_data: dict) -> tuple[bool, list[str]]:
        """Validate Malaysian employee data."""
        errors = []
        
        for field in self.get_required_fields():
            if not employee_data.get(field):
                errors.append(f"Required field '{field}' is missing")
        
        # Validate IC number format if provided (YYMMDD-PB-###G)
        ic = employee_data.get("ic_number")
        if ic and not self._validate_ic(ic):
            errors.append("IC number format invalid (should be YYMMDD-PB-###G)")
        
        return (len(errors) == 0, errors)
    
    def get_tax_id_name(self) -> str:
        """Malaysian tax ID name."""
        return "Income Tax Number"
    
    def get_localization_schema(self) -> dict:
        """JSON schema for Malaysian employee data."""
        return {
            "type": "object",
            "properties": {
                "ic_number": {
                    "type": "string",
                    "pattern": "^[0-9]{6}-[0-9]{2}-[0-9]{4}$",
                    "description": "MyKad/IC number (YYMMDD-PB-###G)"
                },
                "epf_number": {
                    "type": "string",
                    "description": "EPF (Employees Provident Fund) number"
                },
                "socso_number": {
                    "type": "string",
                    "description": "SOCSO (Social Security Organization) number"
                },
                "eis_number": {
                    "type": "string",
                    "description": "EIS (Employment Insurance System) number"
                },
                "race": {
                    "type": "string",
                    "enum": ["Malay", "Chinese", "Indian", "Other"],
                    "description": "Race (commonly required on forms)"
                }
            }
        }
    
    def _validate_ic(self, ic: str) -> bool:
        """Basic IC number validation."""
        import re
        return bool(re.match(r'^\d{6}-\d{2}-\d{4}$', ic))
    
    def get_statutory_requirements(self) -> dict:
        """Get Malaysian employment law requirements."""
        return {
            "minimum_wage_myr": 1500,
            "probation_period_max_months": 3,
            "annual_leave_min_days": 8,  # Increases with tenure
            "notice_period_days": 30,
            "epf_rate_employer": 0.13,
            "epf_rate_employee": 0.11,
        }


@localization_registry.register("SGP", "employees")
class SingaporeEmployeeHandler:
    """Singaporean employee-specific requirements."""
    
    def get_required_fields(self) -> list[str]:
        """Required fields for Singaporean employees."""
        return [
            "first_name",
            "last_name",
            "email",
            "hire_date",
            "tax_id",  # NRIC/FIN
            "nationality",
            "country",
        ]
    
    def get_optional_fields(self) -> list[str]:
        """Optional Singapore-specific fields."""
        return [
            "nric_fin",  # NRIC/FIN number
            "work_permit_type",  # For foreigners: EP, S Pass, Work Permit
            "work_permit_expiry",
            "cpf_number",  # CPF (pension)
            "pr_status",  # Permanent Resident status
        ]
    
    def validate_data(self, employee_data: dict) -> tuple[bool, list[str]]:
        """Validate Singaporean employee data."""
        errors = []
        
        for field in self.get_required_fields():
            if not employee_data.get(field):
                errors.append(f"Required field '{field}' is missing")
        
        # Validate NRIC/FIN format if provided
        nric = employee_data.get("nric_fin")
        if nric and not self._validate_nric(nric):
            errors.append("NRIC/FIN format invalid (should be S/T/F/G#######[A-Z])")
        
        return (len(errors) == 0, errors)
    
    def get_tax_id_name(self) -> str:
        """Singaporean tax ID name."""
        return "NRIC/FIN"
    
    def get_localization_schema(self) -> dict:
        """JSON schema for Singaporean employee data."""
        return {
            "type": "object",
            "properties": {
                "nric_fin": {
                    "type": "string",
                    "pattern": "^[STFG][0-9]{7}[A-Z]$",
                    "description": "NRIC/FIN number"
                },
                "work_permit_type": {
                    "type": "string",
                    "enum": ["Citizen", "PR", "EP", "S Pass", "Work Permit", "Dependent Pass"],
                    "description": "Work authorization type"
                },
                "work_permit_expiry": {
                    "type": "string",
                    "format": "date",
                    "description": "Work permit expiry date (for non-citizens)"
                },
                "cpf_number": {
                    "type": "string",
                    "description": "CPF (Central Provident Fund) number"
                },
                "pr_status": {
                    "type": "boolean",
                    "description": "Permanent Resident status"
                }
            }
        }
    
    def _validate_nric(self, nric: str) -> bool:
        """Basic NRIC/FIN validation."""
        import re
        return bool(re.match(r'^[STFG]\d{7}[A-Z]$', nric))
    
    def get_statutory_requirements(self) -> dict:
        """Get Singaporean employment law requirements."""
        return {
            "minimum_wage_sgd": None,  # No statutory minimum wage
            "probation_period_typical_months": 3,
            "annual_leave_min_days": 7,  # Increases with tenure
            "notice_period_days": 14,  # Varies by tenure
            "cpf_rate_employer_ordinary": 0.17,
            "cpf_rate_employee_ordinary": 0.20,
        }
