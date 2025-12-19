"""
Reference data endpoints for common lookups like currencies, countries, etc.
These provide options for form dropdowns based on system configuration.
Uses the global localization registry for country and currency data.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, distinct
from pydantic import BaseModel

from tera.core.database import get_db
from tera.core.localization import COUNTRY_CODES, CURRENCY_CODES, get_currency_for_country
from tera.modules.company.models import Company

router = APIRouter(prefix="/reference", tags=["reference"])


class CurrencyOption(BaseModel):
    code: str
    name: str
    symbol: str


class CountryOption(BaseModel):
    code: str
    name: str


@router.get("/currencies", response_model=List[CurrencyOption])
async def get_currencies():
    """Get available currency options from global localization registry"""
    currencies = [{
        "code": code,
        "name": info["name"],
        "symbol": info["symbol"]
    } for code, info in CURRENCY_CODES.items()]
    return sorted(currencies, key=lambda x: x["code"])


@router.get("/countries", response_model=List[CountryOption])
async def get_countries():
    """Get available country options from global localization registry"""
    countries = [{
        "code": code,
        "name": name
    } for code, name in COUNTRY_CODES.items()]
    return sorted(countries, key=lambda x: x["name"])


@router.get("/countries/{country_code}/currency")
async def get_country_currency(country_code: str) -> CurrencyOption:
    """Get the primary currency for a specific country"""
    currency_code = get_currency_for_country(country_code)
    currency_info = CURRENCY_CODES[currency_code]

    return {
        "code": currency_code,
        "name": currency_info["name"],
        "symbol": currency_info["symbol"]
    }
