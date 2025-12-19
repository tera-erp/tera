from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import modules
from app.modules.company.router import router as company_module_router
from app.modules.users.router import router as users_module_router
from app.modules.employees.router import router as employees_module_router
from app.core.config import settings


# Module routers (self-contained under app/modules)
from app.modules.finance.router import router as finance_router
from app.modules.payroll.router import router as payroll_router
from app.modules import finance as finance_module
from app.modules import payroll as payroll_module

# Import all models to register them with Base.metadata
# Core models (company, user, employee) are imported in app/modules/core/models.py
# which imports from individual module files and exports via __all__
from app.modules.core.models import (  # noqa: F401
    ModuleSetting,
    Company,
    User,
    EmployeeProfile,
)
from app.modules.finance.models import Partner, Invoice, InvoiceLine, Product  # noqa: F401
from app.modules.payroll.models import PayrollRun, Payslip  # noqa: F401

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
# Register module-wrapped routers for company and users. These wrappers
# include the legacy routers but make them discoverable as modules too.
app.include_router(users_module_router, prefix="/api/v1")
app.include_router(company_module_router, prefix="/api/v1")
app.include_router(employees_module_router, prefix="/api/v1")
app.include_router(modules.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"status": "System Online", "modules": ["Finance", "Payroll"]}

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}