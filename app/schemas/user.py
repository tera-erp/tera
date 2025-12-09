from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.user import UserRole, UserStatus

# Base schema with common fields
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    role: UserRole = UserRole.EMPLOYEE
    status: UserStatus = UserStatus.ACTIVE

# Schema for creating a new user
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    company_id: int

# Schema for updating a user
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)

# Schema for user response (no password)
class UserResponse(UserBase):
    id: int
    company_id: int
    avatar_url: Optional[str] = None
    is_superuser: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Schema for user with employee profile
class UserWithProfile(UserResponse):
    employee_profile: Optional["EmployeeProfileResponse"] = None

    model_config = ConfigDict(from_attributes=True)

# Schema for login
class UserLogin(BaseModel):
    username: str
    password: str

# Schema for token response
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Schema for admin setup during initialization
class AdminSetup(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)
    company_name: str = Field(..., min_length=1, max_length=255)
    country_code: str = Field(..., min_length=2, max_length=2)

# Schema for setup status
class SetupStatus(BaseModel):
    is_initialized: bool
    admin_exists: bool

# Import for forward reference
from app.schemas.employee import EmployeeProfileResponse
UserWithProfile.model_rebuild()
