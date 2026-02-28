"""Pytest configuration and shared fixtures."""
import asyncio
from typing import AsyncGenerator, Generator
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from tera.main import app
from tera.core.database import Base, get_db
from tera.modules.users.models import User, UserRole, UserStatus
from tera.modules.company.models import Company, CompanyStatus
from tera.modules.employees.models import EmployeeProfile, EmployeeStatus
from tera.utils.security import hash_password
from tera.utils.jwt import create_access_token

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/tera_test"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with overridden database dependency."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_company(db_session: AsyncSession) -> Company:
    """Create a test company."""
    company = Company(
        name="Test Company",
        legal_name="Test Company Ltd",
        country_code="USA",
        currency_code="USD",
        timezone="UTC",
        status=CompanyStatus.ACTIVE
    )
    db_session.add(company)
    await db_session.commit()
    await db_session.refresh(company)
    return company


@pytest.fixture
async def test_admin_user(db_session: AsyncSession, test_company: Company) -> User:
    """Create a test admin user."""
    user = User(
        email="admin@test.com",
        username="admin",
        first_name="Admin",
        last_name="User",
        hashed_password=hash_password("testpass123"),
        phone="+1234567890",
        role=UserRole.IT_ADMIN,
        status=UserStatus.ACTIVE,
        company_id=test_company.id,
        is_verified=True,
        is_superuser=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_hr_admin_user(db_session: AsyncSession, test_company: Company) -> User:
    """Create a test HR admin user."""
    user = User(
        email="hradmin@test.com",
        username="hradmin",
        first_name="HR",
        last_name="Admin",
        hashed_password=hash_password("testpass123"),
        phone="+1234567890",
        role=UserRole.HR_ADMIN,
        status=UserStatus.ACTIVE,
        company_id=test_company.id,
        is_verified=True,
        is_superuser=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_employee_user(db_session: AsyncSession, test_company: Company) -> User:
    """Create a test employee user."""
    user = User(
        email="employee@test.com",
        username="employee",
        first_name="Test",
        last_name="Employee",
        hashed_password=hash_password("testpass123"),
        phone="+1234567890",
        role=UserRole.EMPLOYEE,
        status=UserStatus.ACTIVE,
        company_id=test_company.id,
        is_verified=True,
        is_superuser=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_employee_profile(
    db_session: AsyncSession,
    test_company: Company,
    test_employee_user: User
) -> EmployeeProfile:
    """Create a test employee profile."""
    profile = EmployeeProfile(
        user_id=test_employee_user.id,
        company_id=test_company.id,
        employee_number="EMP-001",
        department="Engineering",
        position="Software Developer",
        hire_date="2024-01-01",
        status=EmployeeStatus.ACTIVE
    )
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(profile)
    return profile


@pytest.fixture
def admin_token(test_admin_user: User) -> str:
    """Generate JWT token for admin user."""
    return create_access_token(
        data={
            "sub": str(test_admin_user.id),
            "username": test_admin_user.username,
            "role": test_admin_user.role.value
        }
    )


@pytest.fixture
def hr_admin_token(test_hr_admin_user: User) -> str:
    """Generate JWT token for HR admin user."""
    return create_access_token(
        data={
            "sub": str(test_hr_admin_user.id),
            "username": test_hr_admin_user.username,
            "role": test_hr_admin_user.role.value
        }
    )


@pytest.fixture
def employee_token(test_employee_user: User) -> str:
    """Generate JWT token for employee user."""
    return create_access_token(
        data={
            "sub": str(test_employee_user.id),
            "username": test_employee_user.username,
            "role": test_employee_user.role.value
        }
    )


@pytest.fixture
def auth_headers(admin_token: str) -> dict:
    """Generate authorization headers with admin token."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def hr_auth_headers(hr_admin_token: str) -> dict:
    """Generate authorization headers with HR admin token."""
    return {"Authorization": f"Bearer {hr_admin_token}"}


@pytest.fixture
def employee_auth_headers(employee_token: str) -> dict:
    """Generate authorization headers with employee token."""
    return {"Authorization": f"Bearer {employee_token}"}
