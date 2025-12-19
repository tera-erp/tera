from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from tera.core.database import Base


class ModuleSetting(Base):
    __tablename__ = "module_settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    module_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    company_id: Mapped[Optional[int]] = mapped_column(ForeignKey("companies.id"), nullable=True, index=True)
    key: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    value: Mapped[dict] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<ModuleSetting(module_id={self.module_id} key={self.key} company_id={self.company_id})>"


# Import core models to register them with Base.metadata
from tera.modules.company.models import Company, CompanyStatus  # noqa: F401, E402
from tera.modules.users.models import User, UserRole, UserStatus  # noqa: F401, E402
from tera.modules.employees.models import EmployeeProfile, EmploymentStatus, EmploymentType, PTKPStatus  # noqa: F401, E402
from tera.modules.core.models.module_status import ModuleStatus  # noqa: F401, E402

__all__ = [
    "ModuleSetting",
    "ModuleStatus",
    "Company",
    "CompanyStatus",
    "User",
    "UserRole",
    "UserStatus",
    "EmployeeProfile",
    "EmploymentStatus",
    "EmploymentType",
    "PTKPStatus",
]
