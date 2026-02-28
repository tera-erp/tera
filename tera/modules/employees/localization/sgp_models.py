from typing import Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tera.core.database import Base


class EmployeeProfileSG(Base):
    """
    Singapore-specific employee fields.
    1:1 with EmployeeProfile via employee_id primary key.
    """
    __tablename__ = "employee_profile_sg"

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employee_profiles.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Tax
    tax_id: Mapped[Optional[str]] = mapped_column(String(100))  # e.g., IRAS/Tax ref if you store it
    is_tax_resident: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Statutory ID
    cpf_number: Mapped[Optional[str]] = mapped_column(String(100))

    # Relationship back to EmployeeProfile
    employee: Mapped["EmployeeProfile"] = relationship(
        "EmployeeProfile",
        back_populates="sgp",
        uselist=False,
    )
