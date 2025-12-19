"""Module status tracking for enabled/disabled modules"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from tera.core.database import Base


class ModuleStatus(Base):
    """Track which modules are enabled/disabled per company"""
    __tablename__ = "module_status"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    module_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    company_id: Mapped[Optional[int]] = mapped_column(ForeignKey("companies.id"), nullable=True, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Metadata
    enabled_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    enabled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    disabled_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    disabled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<ModuleStatus(module_id={self.module_id} enabled={self.enabled} company_id={self.company_id})>"
