"""Global localization registry for country-specific implementations.

This module provides a central registry for country-specific behaviors across different
modules (employees, payroll, etc.). Each module can register its own localization handlers
for specific countries using standard ISO 3166-1 alpha-3 country codes.

Example:
    # In payroll module
    @localization_registry.register("IDN", "payroll")
    class IndonesiaPayrollHandler:
        def calculate_taxes(self, gross: Decimal) -> Decimal:
            ...
    
    # In employees module
    @localization_registry.register("IDN", "employees")
    class IndonesiaEmployeeHandler:
        def get_required_fields(self) -> list[str]:
            return ["npwp", "bpjs_kesehatan"]
"""
from typing import Any, Dict, Optional, Protocol, Type
from dataclasses import dataclass


# Standard ISO 3166-1 alpha-3 country codes
COUNTRY_CODES = {
    "IDN": "Indonesia",
    "MYS": "Malaysia", 
    "SGP": "Singapore",
    "USA": "United States",
    "GBR": "United Kingdom",
    "AUS": "Australia",
    "JPN": "Japan",
    "CHN": "China",
    "IND": "India",
    "DEU": "Germany",
    "FRA": "France",
    "ITA": "Italy",
    "ESP": "Spain",
    "THA": "Thailand",
    "VNM": "Vietnam",
    "PHL": "Philippines",
    "CAN": "Canada",
    "BRA": "Brazil",
    "MEX": "Mexico",
    "NLD": "Netherlands",
}

# ISO 4217 Currency codes with symbols
CURRENCY_CODES = {
    "USD": {"name": "US Dollar", "symbol": "$", "countries": ["USA"]},
    "EUR": {"name": "Euro", "symbol": "€", "countries": ["DEU", "FRA", "ITA", "ESP", "NLD"]},
    "GBP": {"name": "British Pound", "symbol": "£", "countries": ["GBR"]},
    "JPY": {"name": "Japanese Yen", "symbol": "¥", "countries": ["JPN"]},
    "CNY": {"name": "Chinese Yuan", "symbol": "¥", "countries": ["CHN"]},
    "INR": {"name": "Indian Rupee", "symbol": "₹", "countries": ["IND"]},
    "IDR": {"name": "Indonesian Rupiah", "symbol": "Rp", "countries": ["IDN"]},
    "SGD": {"name": "Singapore Dollar", "symbol": "S$", "countries": ["SGP"]},
    "MYR": {"name": "Malaysian Ringgit", "symbol": "RM", "countries": ["MYS"]},
    "THB": {"name": "Thai Baht", "symbol": "฿", "countries": ["THA"]},
    "VND": {"name": "Vietnamese Dong", "symbol": "₫", "countries": ["VNM"]},
    "PHP": {"name": "Philippine Peso", "symbol": "₱", "countries": ["PHL"]},
    "AUD": {"name": "Australian Dollar", "symbol": "A$", "countries": ["AUS"]},
    "CAD": {"name": "Canadian Dollar", "symbol": "C$", "countries": ["CAN"]},
    "CHF": {"name": "Swiss Franc", "symbol": "CHF", "countries": []},
    "BRL": {"name": "Brazilian Real", "symbol": "R$", "countries": ["BRA"]},
    "MXN": {"name": "Mexican Peso", "symbol": "MX$", "countries": ["MEX"]},
}


def get_currency_for_country(country_code: str) -> str:
    """Get the primary currency code for a country.
    
    Args:
        country_code: ISO 3166-1 alpha-3 country code
    
    Returns:
        ISO 4217 currency code
    """
    country = country_code.upper()
    for currency, info in CURRENCY_CODES.items():
        if country in info.get("countries", []):
            return currency
    return "USD"  # Default fallback


@dataclass
class LocalizationHandler:
    """Container for a localization handler."""
    country_code: str
    domain: str  # e.g., "payroll", "employees", "tax", "benefits"
    handler_class: Type
    handler_instance: Optional[Any] = None
    
    def get_instance(self) -> Any:
        """Lazy instantiation of handler."""
        if self.handler_instance is None:
            self.handler_instance = self.handler_class()
        return self.handler_instance


class LocalizationRegistry:
    """Global registry for country-specific implementations across modules.
    
    Structure: {country_code: {domain: LocalizationHandler}}
    """
    
    def __init__(self):
        self._handlers: Dict[str, Dict[str, LocalizationHandler]] = {}
        self._default_handlers: Dict[str, LocalizationHandler] = {}
    
    def register(self, country_code: str, domain: str):
        """Decorator to register a localization handler.
        
        Args:
            country_code: ISO 3166-1 alpha-3 code (e.g., "IDN", "MYS", "SGP")
            domain: Module domain (e.g., "payroll", "employees", "tax")
        
        Example:
            @localization_registry.register("IDN", "payroll")
            class IndonesiaPayrollHandler:
                ...
        """
        def decorator(handler_class: Type) -> Type:
            country = country_code.upper()
            
            if country not in self._handlers:
                self._handlers[country] = {}
            
            handler = LocalizationHandler(
                country_code=country,
                domain=domain,
                handler_class=handler_class
            )
            self._handlers[country][domain] = handler
            
            return handler_class
        return decorator
    
    def register_default(self, domain: str):
        """Register a default handler for a domain when no country-specific one exists.
        
        Args:
            domain: Module domain (e.g., "payroll", "employees")
        
        Example:
            @localization_registry.register_default("payroll")
            class DefaultPayrollHandler:
                ...
        """
        def decorator(handler_class: Type) -> Type:
            handler = LocalizationHandler(
                country_code="DEFAULT",
                domain=domain,
                handler_class=handler_class
            )
            self._default_handlers[domain] = handler
            return handler_class
        return decorator
    
    def get(self, country_code: str, domain: str) -> Optional[Any]:
        """Get a localization handler instance.
        
        Args:
            country_code: ISO 3166-1 alpha-3 code
            domain: Module domain
        
        Returns:
            Handler instance or None if not found
        """
        country = country_code.upper()
        
        # Try country-specific handler
        if country in self._handlers and domain in self._handlers[country]:
            return self._handlers[country][domain].get_instance()
        
        # Fall back to default handler
        if domain in self._default_handlers:
            return self._default_handlers[domain].get_instance()
        
        return None
    
    def get_or_raise(self, country_code: str, domain: str) -> Any:
        """Get a localization handler or raise an error.
        
        Args:
            country_code: ISO 3166-1 alpha-3 code
            domain: Module domain
        
        Returns:
            Handler instance
        
        Raises:
            ValueError: If no handler is found
        """
        handler = self.get(country_code, domain)
        if handler is None:
            raise ValueError(
                f"No localization handler found for country='{country_code}' domain='{domain}'"
            )
        return handler
    
    def has_handler(self, country_code: str, domain: str) -> bool:
        """Check if a handler exists for the given country and domain."""
        country = country_code.upper()
        return (
            country in self._handlers 
            and domain in self._handlers[country]
        ) or domain in self._default_handlers
    
    def list_countries(self, domain: Optional[str] = None) -> list[str]:
        """List all countries with registered handlers.
        
        Args:
            domain: Optional domain filter
        
        Returns:
            List of country codes
        """
        if domain:
            return [
                country 
                for country, domains in self._handlers.items()
                if domain in domains
            ]
        return list(self._handlers.keys())
    
    def list_domains(self, country_code: Optional[str] = None) -> list[str]:
        """List all registered domains.
        
        Args:
            country_code: Optional country filter
        
        Returns:
            List of domain names
        """
        if country_code:
            country = country_code.upper()
            if country in self._handlers:
                return list(self._handlers[country].keys())
            return []
        
        # Collect all unique domains
        domains = set()
        for country_handlers in self._handlers.values():
            domains.update(country_handlers.keys())
        domains.update(self._default_handlers.keys())
        return sorted(domains)
    
    def get_info(self) -> Dict[str, Any]:
        """Get registry information for debugging."""
        return {
            "countries": {
                country: list(domains.keys())
                for country, domains in self._handlers.items()
            },
            "default_domains": list(self._default_handlers.keys()),
            "total_handlers": sum(
                len(domains) for domains in self._handlers.values()
            ) + len(self._default_handlers)
        }


# Global singleton instance
localization_registry = LocalizationRegistry()


# Protocols for different domains
class PayrollLocalization(Protocol):
    """Protocol for payroll localization handlers."""
    
    def calculate_taxes(self, gross_salary: float, employee_data: dict) -> dict:
        """Calculate taxes and deductions."""
        ...
    
    def calculate_contributions(self, gross_salary: float, employee_data: dict) -> dict:
        """Calculate employer contributions."""
        ...


class EmployeeLocalization(Protocol):
    """Protocol for employee localization handlers."""
    
    def get_required_fields(self) -> list[str]:
        """Get list of required country-specific fields."""
        ...
    
    def get_optional_fields(self) -> list[str]:
        """Get list of optional country-specific fields."""
        ...
    
    def validate_data(self, employee_data: dict) -> tuple[bool, list[str]]:
        """Validate country-specific employee data.
        
        Returns:
            (is_valid, error_messages)
        """
        ...
    
    def get_tax_id_name(self) -> str:
        """Get the name of the tax ID for this country."""
        ...


class BenefitsLocalization(Protocol):
    """Protocol for benefits/leave localization handlers."""
    
    def get_statutory_leave_days(self) -> dict[str, int]:
        """Get statutory leave entitlements."""
        ...
    
    def get_public_holidays(self, year: int) -> list[dict]:
        """Get public holidays for the year."""
        ...


class ComplianceLocalization(Protocol):
    """Protocol for compliance/regulatory requirements."""
    
    def get_minimum_wage(self, region: Optional[str] = None) -> float:
        """Get minimum wage for the country/region."""
        ...
    
    def get_working_hours_limits(self) -> dict:
        """Get working hours regulations."""
        ...
