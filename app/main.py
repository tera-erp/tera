from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, companies, employees, modules
from app.core.config import settings
from app.core.database import Base, engine

# Module routers (self-contained under app/modules)
from app.modules.finance.router import router as finance_router
from app.modules.payroll.router import router as payroll_router
from app.modules import finance as finance_module
from app.modules import payroll as payroll_module

# Import module models to register them
from app.modules.finance.models import Partner, Invoice, InvoiceLine, Product  # noqa: F401
from app.modules.payroll.models import PayrollRun, Payslip  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.company import Company  # noqa: F401
from app.models.employee import EmployeeProfile  # noqa: F401

app = FastAPI(title="Tera ERP Backend", version="1.0.0")

# Initialize module system
modules.initialize_modules()
finance_module.register_actions()
payroll_module.register_actions()

# CORS Middleware - Allow frontend to communicate with backend
# Convert CORS origins from settings (which are pydantic AnyHttpUrl objects) to strings
cors_origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS] if settings.BACKEND_CORS_ORIGINS else []
# Add defaults for development
if not cors_origins:
    cors_origins = ["http://localhost:8080", "http://127.0.0.1:8080", "http://frontend:8080"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers with /api/v1 prefix
app.include_router(finance_router, prefix="/api/v1")
app.include_router(payroll_router, prefix="/api/v1/payroll")
app.include_router(users.router, prefix="/api/v1")
app.include_router(companies.router, prefix="/api/v1")
app.include_router(employees.router, prefix="/api/v1")
app.include_router(modules.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"status": "System Online", "modules": ["Finance", "Payroll"]}

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}