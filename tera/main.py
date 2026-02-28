from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from pathlib import Path

from tera.core.config import settings
from tera.modules.core import registry
from tera.routers import modules
from . import VERSION


class ModuleStatusMiddleware(BaseHTTPMiddleware):
    """Middleware to check if a module is enabled before processing requests"""

    async def dispatch(self, request: Request, call_next):
        # Extract module name from path
        path = request.url.path

        # Skip checks for non-module endpoints
        if not path.startswith('/api/v1/'):
            return await call_next(request)

        # Skip checks for system endpoints
        system_endpoints = ['/api/v1/users', '/api/v1/companies', '/api/v1/modules', '/api/v1/health']
        if any(path.startswith(endpoint) for endpoint in system_endpoints):
            return await call_next(request)

        # Extract module name from path (e.g., /api/v1/finance/... -> finance)
        parts = path.split('/')
        if len(parts) > 3:

            # Import here to avoid circular imports
            from tera.modules.core.models import ModuleStatus
            from sqlalchemy import select
            from tera.core.database import AsyncSessionLocal

            # Check if module is enabled
            try:
                async with AsyncSessionLocal() as db:
                    stmt = select(ModuleStatus).where(
                        ModuleStatus.module_id == module_name
                    )
                    result = await db.execute(stmt)
                    status = result.scalar_one_or_none()

                    # If status exists and module is disabled, block access
                    if status is not None and not status.enabled:
                        return JSONResponse(
                            status_code=403,
                            content={
                                "detail": f"Module '{module_name}' is disabled. Enable it in Settings to access this functionality."
                            }
                        )
            except Exception as e:
                # Log error but allow request to proceed to avoid breaking the app
                print(f"Error checking module status for {module_name}: {e}")

        return await call_next(request)


# Initialize FastAPI app
app = FastAPI(title="Tera Backend", version=VERSION)

# Initialize module system - discovers and registers all modules automatically
modules_dir = Path(__file__).parent / "modules"
registry.initialize(modules_dir)

# Initialize module configs for the modules router
modules.initialize_modules()

# Initialize localizations - register all country-specific handlers
from tera.modules.employees import localization as employee_localization  # noqa: F401
from tera.modules.payroll import localization as payroll_localization  # noqa: F401

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

# Add module status check middleware
app.add_middleware(ModuleStatusMiddleware)

# Dynamically include all registered module routers
for module_name, router in registry.get_routers().items():
    # Determine prefix based on module
    prefix = f"/api/v1/{module_name}" if module_name not in ["users", "company", "companies"] else "/api/v1"

    # Special case: payroll needs /api/v1/payroll prefix
    if module_name == "payroll":
        prefix = "/api/v1/payroll"

    app.include_router(router, prefix=prefix)
    print(f"Registered router: {module_name} at {prefix}")

# Include the modules system router
app.include_router(modules.router, prefix="/api/v1")

# Include reference data router for common lookups
from tera.routers import reference
app.include_router(reference.router, prefix="/api/v1")

# Include localization router for country-specific requirements
from tera.routers import localization
app.include_router(localization.router, prefix="/api/v1")

@app.get("/")
async def root():
    module_list = list(registry.get_configs().keys())
    return {"status": "System Online", "modules": module_list}

@app.get("/health")
@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy", 
        "version": VERSION,
        "modules_loaded": len(registry.get_configs())
    }