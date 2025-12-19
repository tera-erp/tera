import enum
from sqlalchemy import Enum as SQLEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from tera.core.database import Base
from typing import Optional

class PTKPStatus(str, enum.Enum):
    TK0 = "TK0"
    TK1 = "TK1"
    TK2 = "TK2"
    TK3 = "TK3"
    K0 = "K0"
    K1 = "K1"
    K2 = "K2"
    K3 = "K3"

class EmployeeProfileID(Base):
    __tablename__ = "employee_profile_id"

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employee_profiles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tax_id_name: str = "NPWP"  # Indonesian Tax ID Name
    ptkp_status: Mapped[Optional[PTKPStatus]] = mapped_column(SQLEnum(PTKPStatus, name="ptkp_status"))
    is_tax_resident: Mapped[bool] = mapped_column(default=True, nullable=False)

    bpjs_kesehatan_number: Mapped[Optional[str]] = mapped_column(String(100))
    bpjs_ketenagakerjaan_number: Mapped[Optional[str]] = mapped_column(String(100))

    employee: Mapped["EmployeeProfile"] = relationship("EmployeeProfile", back_populates="idn")
