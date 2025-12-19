from typing import List, Optional
from datetime import datetime
import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import ProgrammingError

from app.core.database import get_db, engine, Base
from .models import User
from .models import UserRole, UserStatus
from app.modules.employees.models import EmployeeProfile
from app.modules.company.models import CompanyStatus, Company
from .schema import (
    UserCreate, 
    UserUpdate, 
    UserResponse, 
    UserWithProfile,
    UserLogin,
    Token,
    AdminSetup,
    SetupStatus
)
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token, decode_access_token

router = APIRouter(prefix="/users", tags=["users"])

# Ensure database schema exists (useful for first-time setup when tables are missing)
async def ensure_schema_initialized():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Helper function to generate employee number
async def generate_employee_number(company_id: int, db: AsyncSession) -> str:
    """Generate a unique employee number for a company"""
    result = await db.execute(
        select(func.count(EmployeeProfile.id)).where(EmployeeProfile.company_id == company_id)
    )
    count = result.scalar() or 0
    return f"EMP-{company_id}-{count + 1:05d}"

# Dependency to get current user from JWT token
async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Extract and validate JWT token, return current user"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = int(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user

# Dependency to check if user is admin
async def check_admin(current_user: User = Depends(get_current_user)) -> User:
    """Verify that current user is an admin (IT_ADMIN or HR_ADMIN)"""
    if current_user.role not in [UserRole.IT_ADMIN, UserRole.HR_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Dependency to check if user is IT admin (superuser)
async def check_it_admin(current_user: User = Depends(get_current_user)) -> User:
    """Verify that current user is an IT admin"""
    if current_user.role != UserRole.IT_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="IT Admin access required"
        )
    return current_user

@router.post("/companies/{company_id}", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_company_user(
    company_id: int,
    user_data: UserCreate,
    current_user: User = Depends(check_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new user for a specific company (Admin only)"""
    # Verify the requesting user is from the same company (or is IT admin)
    if current_user.role != UserRole.IT_ADMIN and current_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create users for other companies"
        )
    
    # Verify company exists
    result = await db.execute(select(Company).where(Company.id == company_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Ensure user_data.company_id matches the URL parameter
    user_data.company_id = company_id
    
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_pwd = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_pwd,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        role=user_data.role,
        status=user_data.status,
        company_id=user_data.company_id,
    )
    
    db.add(user)
    await db.flush()  # Ensure user ID is generated
    
    # Auto-create employee profile if user is not an admin
    if user_data.role not in [UserRole.IT_ADMIN, UserRole.HR_ADMIN]:
        employee_number = await generate_employee_number(company_id, db)
        employee = EmployeeProfile(
            user_id=user.id,
            company_id=company_id,
            employee_number=employee_number,
            employment_status="active",
            employment_type="full_time",
            hire_date=dt.date.today()
        )
        db.add(employee)
    
    await db.commit()
    await db.refresh(user)
    
    return user

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new user (public endpoint - kept for backward compatibility)"""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_pwd = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_pwd,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        role=user_data.role,
        status=user_data.status,
        company_id=user_data.company_id,
    )
    
    db.add(user)
    await db.flush()  # Ensure user ID is generated
    
    # Auto-create employee profile if user has a company and is not an admin
    if user_data.company_id and user_data.role not in [UserRole.IT_ADMIN, UserRole.HR_ADMIN]:
        employee_number = await generate_employee_number(user_data.company_id, db)
        employee = EmployeeProfile(
            user_id=user.id,
            company_id=user_data.company_id,
            employee_number=employee_number,
            employment_status="active",
            employment_type="full_time",
            hire_date=dt.date.today()
        )
        db.add(employee)
    
    await db.commit()
    await db.refresh(user)
    
    return user

# ============================================================================
# SETUP ENDPOINTS - For first-time initialization
# ============================================================================

@router.get("/setup/status", response_model=SetupStatus)
async def get_setup_status(db: AsyncSession = Depends(get_db)):
    """Check if the system has been initialized with an admin account"""
    # Check if any IT_ADMIN users exist; if tables are missing, create them on the fly
    try:
        result = await db.execute(
            select(func.count(User.id)).where(User.role == UserRole.IT_ADMIN)
        )
        admin_count = result.scalar()
    except ProgrammingError:
        # Auto-create schema and retry once
        await ensure_schema_initialized()
        result = await db.execute(
            select(func.count(User.id)).where(User.role == UserRole.IT_ADMIN)
        )
        admin_count = result.scalar()
    
    return SetupStatus(
        is_initialized=admin_count > 0,
        admin_exists=admin_count > 0
    )

@router.post("/setup/admin", response_model=Token, status_code=status.HTTP_201_CREATED)
async def setup_admin(
    setup_data: AdminSetup,
    db: AsyncSession = Depends(get_db)
):
    """Create the first admin account and company (only allowed if no admin exists)"""
    # Ensure schema exists before proceeding (handles fresh DBs without tables)
    try:
        result = await db.execute(
            select(func.count(User.id)).where(User.role == UserRole.IT_ADMIN)
        )
        admin_count = result.scalar()
    except ProgrammingError:
        await ensure_schema_initialized()
        result = await db.execute(
            select(func.count(User.id)).where(User.role == UserRole.IT_ADMIN)
        )
        admin_count = result.scalar()
    
    if admin_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin account already exists. System is already initialized."
        )
    
    # Check if username or email already exists
    existing_user = await db.execute(
        select(User).where(
            (User.username == setup_data.username) | 
            (User.email == setup_data.email)
        )
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    
    # Create company
    company = Company(
        name=setup_data.company_name,
        legal_name=setup_data.company_name,
        country_code=setup_data.country_code,
        currency_code="USD",  # Default, can be customized later
        timezone="UTC",  # Default, can be customized later
        status=CompanyStatus.ACTIVE
    )
    db.add(company)
    await db.flush()  # Get company ID without committing
    
    # Create admin user
    user = User(
        email=setup_data.email,
        username=setup_data.username,
        first_name=setup_data.first_name,
        last_name=setup_data.last_name,
        hashed_password=hash_password(setup_data.password),
        phone="",
        role=UserRole.IT_ADMIN,
        status=UserStatus.ACTIVE,
        company_id=company.id,
        is_verified=True,
        is_superuser=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role.value}
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return access token"""
    # Find user by username
    result = await db.execute(
        select(User).where(User.username == login_data.username)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role.value}
    )
    
    return Token(access_token=access_token, user=UserResponse.model_validate(user))

@router.get("/companies/{company_id}/", response_model=List[UserResponse])
async def list_company_users(
    company_id: int,
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all users in a company (must be from same company or IT admin)"""
    # Verify the requesting user can access this company
    if current_user.role != UserRole.IT_ADMIN and current_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view users from other companies"
        )
    
    # Verify company exists
    result = await db.execute(select(Company).where(Company.id == company_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    query = select(User).where(User.company_id == company_id).offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return users

@router.get("/", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(get_current_user),
    company_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List users - returns own company users unless IT admin"""
    # If no company_id specified, use current user's company (unless IT admin)
    if not company_id:
        if current_user.role == UserRole.IT_ADMIN:
            # IT admins can see all users across all companies
            query = select(User).offset(skip).limit(limit)
        else:
            # Regular users see only their company's users
            company_id = current_user.company_id
            query = select(User).where(User.company_id == company_id).offset(skip).limit(limit)
    else:
        # If company_id specified, verify access
        if current_user.role != UserRole.IT_ADMIN and current_user.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view users from other companies"
            )
        query = select(User).where(User.company_id == company_id).offset(skip).limit(limit)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return users

@router.get("/{user_id}", response_model=UserWithProfile)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific user by ID with their employee profile"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check access: can view if same company or IT admin
    if current_user.role != UserRole.IT_ADMIN and current_user.company_id != user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view users from other companies"
        )
    
    # Fetch employee profile if exists
    if user.employee_profile:
        await db.refresh(user, ["employee_profile"])
    
    return user

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a user (own profile or admin)"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check access: can update if own profile or admin
    is_own_profile = current_user.id == user_id
    is_admin = current_user.role in [UserRole.IT_ADMIN, UserRole.HR_ADMIN]
    is_same_company = current_user.company_id == user.company_id
    
    if not is_own_profile and not (is_admin and is_same_company):
        if current_user.role != UserRole.IT_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update other users"
            )
    
    # Update fields
    update_data = user_data.model_dump(exclude_unset=True)
    
    # Handle password separately
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    
    return user

@router.put("/{user_id}/company/{company_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def assign_user_to_company(
    user_id: int,
    company_id: int,
    current_user: User = Depends(check_admin),
    db: AsyncSession = Depends(get_db)
):
    """Assign a user to a company (Admin only)"""
    # Get the user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify the company exists
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Check authorization: only IT admin can assign to any company, HR admin can only assign within their company
    if current_user.role == UserRole.HR_ADMIN and current_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR Admins can only assign users to their own company"
        )
    
    # If user is being moved to a different company, update/create employee profile
    old_company_id = user.company_id
    user.company_id = company_id
    
    # If user is not an admin, ensure they have an employee profile in the new company
    if user.role not in [UserRole.IT_ADMIN, UserRole.HR_ADMIN]:
        # Check if employee profile exists for this user in the new company
        result = await db.execute(
            select(EmployeeProfile).where(
                (EmployeeProfile.user_id == user_id) & 
                (EmployeeProfile.company_id == company_id)
            )
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            # Create new employee profile for the new company
            employee_number = await generate_employee_number(company_id, db)
            employee = EmployeeProfile(
                user_id=user_id,
                company_id=company_id,
                employee_number=employee_number,
                employment_status="active",
                employment_type="full_time",
                hire_date=dt.date.today()
            )
            db.add(employee)
    
    await db.commit()
    await db.refresh(user)
    
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(check_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete a user (Admin only)"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check access: can delete if same company or IT admin
    if current_user.role != UserRole.IT_ADMIN and current_user.company_id != user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete users from other companies"
        )
    
    await db.delete(user)
    await db.commit()
    
    return None
