from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from tera.core.database import Base
from tera.modules.company.models import Company
import enum


class UserRole(str, enum.Enum):
    """User roles in the system"""
    ADMIN = "admin"
    HR_ADMIN = "hr_admin"
    IT_ADMIN = "it_admin"
    EMPLOYEE = "employee"
    VIEWER = "viewer"


class UserStatus(str, enum.Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255),
                                       unique=True,
                                       index=True,
                                       nullable=False)
    username: Mapped[str] = mapped_column(String(100),
                                          unique=True,
                                          index=True,
                                          nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profile Information
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Role and Status
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole),
                                           default=UserRole.EMPLOYEE,
                                           nullable=False)
    status: Mapped[UserStatus] = mapped_column(SQLEnum(UserStatus),
                                               default=UserStatus.ACTIVE,
                                               nullable=False)

    # Company Association
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"),
                                            nullable=False,
                                            index=True)

    # Flags
    is_superuser: Mapped[bool] = mapped_column(Boolean,
                                               default=False,
                                               nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean,
                                              default=False,
                                              nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime,
                                                 default=datetime.now(timezone.utc),
                                                 nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime,
                                                 default=datetime.now(timezone.utc),
                                                 onupdate=datetime.now(timezone.utc),
                                                 nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    company: Mapped[Company] = relationship(Company, back_populates="users")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
