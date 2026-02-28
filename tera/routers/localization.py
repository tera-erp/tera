"""Localization API endpoints.

Provides information about available country-specific handlers and their requirements.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from tera.core.localization import localization_registry, COUNTRY_CODES

router = APIRouter(prefix="/localization", tags=["localization"])


@router.get("/countries")
async def list_countries() -> Dict[str, str]:
    """Get list of supported countries with ISO codes."""
    return COUNTRY_CODES


@router.get("/domains")
async def list_domains() -> Dict[str, Any]:
    """Get list of all registered localization domains."""
    return {
        "domains": localization_registry.list_domains(),
        "info": localization_registry.get_info()
    }


@router.get("/countries/{country_code}/domains")
async def get_country_domains(country_code: str) -> Dict[str, Any]:
    """Get all available localization domains for a specific country."""
    country = country_code.upper()
    
    if country not in COUNTRY_CODES:
        raise HTTPException(status_code=404, detail=f"Country code '{country_code}' not recognized")
    
    domains = localization_registry.list_domains(country)
    
    return {
        "country_code": country,
        "country_name": COUNTRY_CODES[country],
        "available_domains": domains,
    }


@router.get("/countries/{country_code}/employees/requirements")
async def get_employee_requirements(country_code: str) -> Dict[str, Any]:
    """Get employee data requirements for a specific country."""
    country = country_code.upper()
    
    handler = localization_registry.get(country, "employees")
    if not handler:
        raise HTTPException(
            status_code=404, 
            detail=f"No employee localization found for country '{country_code}'"
        )
    
    return {
        "country_code": country,
        "country_name": COUNTRY_CODES.get(country, "Unknown"),
        "required_fields": handler.get_required_fields(),
        "optional_fields": handler.get_optional_fields(),
        "tax_id_name": handler.get_tax_id_name(),
        "localization_schema": handler.get_localization_schema(),
    }


@router.get("/countries/{country_code}/employees/statutory")
async def get_statutory_requirements(country_code: str) -> Dict[str, Any]:
    """Get statutory employment requirements for a specific country."""
    country = country_code.upper()
    
    handler = localization_registry.get(country, "employees")
    if not handler:
        raise HTTPException(
            status_code=404,
            detail=f"No employee localization found for country '{country_code}'"
        )
    
    # Check if handler has statutory requirements method
    if not hasattr(handler, 'get_statutory_requirements'):
        return {
            "country_code": country,
            "country_name": COUNTRY_CODES.get(country, "Unknown"),
            "statutory_requirements": None,
        }
    
    return {
        "country_code": country,
        "country_name": COUNTRY_CODES.get(country, "Unknown"),
        "statutory_requirements": handler.get_statutory_requirements(),
    }


@router.post("/countries/{country_code}/employees/validate")
async def validate_employee_data(
    country_code: str,
    employee_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Validate employee data against country-specific requirements."""
    country = country_code.upper()
    
    handler = localization_registry.get(country, "employees")
    if not handler:
        raise HTTPException(
            status_code=404,
            detail=f"No employee localization found for country '{country_code}'"
        )
    
    is_valid, errors = handler.validate_data(employee_data)
    
    return {
        "country_code": country,
        "is_valid": is_valid,
        "errors": errors,
    }


@router.get("/domains/{domain}/countries")
async def get_domain_countries(domain: str) -> Dict[str, Any]:
    """Get all countries that have handlers for a specific domain."""
    countries = localization_registry.list_countries(domain)
    
    if not countries:
        raise HTTPException(
            status_code=404,
            detail=f"No countries found with '{domain}' localization"
        )
    
    return {
        "domain": domain,
        "countries": [
            {
                "code": code,
                "name": COUNTRY_CODES.get(code, "Unknown")
            }
            for code in countries
        ]
    }


@router.get("/")
async def get_localization_info() -> Dict[str, Any]:
    """Get complete localization registry information."""
    info = localization_registry.get_info()
    
    return {
        **info,
        "available_countries": {
            code: name for code, name in COUNTRY_CODES.items()
            if code in info["countries"]
        }
    }
