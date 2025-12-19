from typing import Optional
from sqlalchemy import String, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from tera.core.database import Base


class MYTaxCategory(str, enum.Enum):
    """Optional: if you want a typed category for tax handling"""
    RESIDENT = "resident"
    NON_RESIDENT = "non_resident"


class EmployeeProfileMY(Base):
    """
    Malaysia-specific employee fields.
    1:1 with EmployeeProfile via employee_id primary key.
    """
    __tablename__ = "employee_profile_my"

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employee_profiles.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Tax
    tax_id: Mapped[Optional[str]] = mapped_column(String(100))  # e.g., TIN if you store it
    is_tax_resident: Mapped[bool] = mapped_column(default=True, nullable=False)
    tax_category: Mapped[Optional[MYTaxCategory]] = mapped_column(
        SQLEnum(MYTaxCategory, name="my_tax_category")
    )

    # Statutory IDs
    epf_number: Mapped[Optional[str]] = mapped_column(String(100))   # KWSP/EPF
    socso_number: Mapped[Optional[str]] = mapped_column(String(100)) # PERKESO/SOCSO
    eis_number: Mapped[Optional[str]] = mapped_column(String(100))   # Optional: EIS if you track separately

    # Relationship back to EmployeeProfile
    employee: Mapped["EmployeeProfile"] = relationship(
        "EmployeeProfile",
        back_populates="mys",
        uselist=False,
    )
