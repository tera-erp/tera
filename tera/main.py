from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from tera.core.config import settings
from tera.modules.core import registry
from tera.routers import modules
from . import VERSION

# Initialize FastAPI app
app = FastAPI(title="Tera Backend", version=VERSION)

# Initialize module system - discovers and registers all modules automatically
modules_dir = Path(__file__).parent / "modules"
registry.initialize(modules_dir)

# Initialize module configs for the modules router
modules.initialize_modules()

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

@app.get("/")
async def root():
    module_list = list(registry.get_configs().keys())
    return {"status": "System Online", "modules": module_list}

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy", 
        "version": VERSION,
        "modules_loaded": len(registry.get_configs())
    }