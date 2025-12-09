"""
Modules router - API endpoints for module system
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

from app.core.database import get_db
from app.modules.core import ModuleLoader, ModuleConfig

router = APIRouter(prefix="/modules", tags=["modules"])

# Module registry (populated at startup)
_module_configs: dict[str, dict] = {}

def initialize_modules():
    """Initialize module registry by loading all module configs"""
    global _module_configs
    
    modules_dir = Path(__file__).parent.parent / "modules"
    
    try:
        configs = ModuleLoader.load_all(modules_dir)
        for module_id, config in configs.items():
            _module_configs[module_id] = config.model_dump()
        print(f"✓ Loaded {len(_module_configs)} modules")
    except Exception as e:
        print(f"Warning: Failed to load modules: {e}")


@router.get("/")
async def list_modules(db: AsyncSession = Depends(get_db)):
    """
    List all available modules and their configurations.
    
    Returns module metadata including screens, forms, workflows, and permissions.
    """
    # Return module configs (sorted by name)
    modules = sorted(_module_configs.values(), key=lambda m: m['module']['name'])
    return modules


@router.get("/{module_id}")
async def get_module(
    module_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get configuration for a specific module.
    
    Includes all screens, forms, workflows, and actions.
    """
    if module_id not in _module_configs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module '{module_id}' not found"
        )
    
    return _module_configs[module_id]


@router.get("/{module_id}/screens")
async def get_module_screens(
    module_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all screens for a module"""
    if module_id not in _module_configs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module '{module_id}' not found"
        )
    
    config = _module_configs[module_id]
    return config.get('screens', {})


@router.get("/{module_id}/workflows")
async def get_module_workflows(
    module_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all workflows for a module"""
    if module_id not in _module_configs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module '{module_id}' not found"
        )
    
    config = _module_configs[module_id]
    return config.get('workflows', {})


@router.get("/{module_id}/permissions")
async def get_module_permissions(
    module_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all permissions defined by a module"""
    if module_id not in _module_configs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module '{module_id}' not found"
        )
    
    config = _module_configs[module_id]
    return config.get('permissions', [])
