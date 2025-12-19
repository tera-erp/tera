"""
Modules router - API endpoints for module system
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path
from pydantic import BaseModel
import importlib
import inspect

from tera.core.database import get_db
from tera.modules.core import registry
from tera.modules.core.models import ModuleSetting

router = APIRouter(prefix="/modules", tags=["modules"])

# Module registry (populated at startup) - now uses the global registry
_module_configs: dict[str, dict] = {}


class ModuleStatusUpdate(BaseModel):
    enabled: bool
    company_id: Optional[int] = None

def initialize_modules():
    """Initialize module registry by loading all module configs from the global registry"""
    global _module_configs
    
    try:
        # Use the global registry instead of loading again
        configs = registry.get_configs()
        for module_id, config in configs.items():
            _module_configs[module_id] = config.model_dump()
        print(f"✓ Module router initialized with {len(_module_configs)} module configs")
    except Exception as e:
        print(f"Warning: Failed to initialize module router: {e}")


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


@router.get("/{module_id}/configurables")
async def get_module_configurables(module_id: str, db: AsyncSession = Depends(get_db)):
    """Return persisted configurables for a module (merged into declared defaults)."""
    if module_id not in _module_configs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Module '{module_id}' not found")

    # Load declared configurables
    config = _module_configs[module_id]
    declared = (config.get('configurables') or {})

    # Load persisted values (global / company-agnostic for now)
    result = await db.execute(select(ModuleSetting).where(ModuleSetting.module_id == module_id))
    rows = result.scalars().all()
    persisted = {r.key: r.value for r in rows}

    # Merge: persisted overrides declared defaults
    merged = {}
    # declared can be array or object
    if isinstance(declared, dict):
        for k, v in declared.items():
            default = None
            if isinstance(v, dict):
                default = v.get('value', v.get('default'))
            else:
                default = v
            merged[k] = persisted.get(k, default)
    elif isinstance(declared, list):
        for item in declared:
            key = item.get('key') or item.get('id')
            default = item.get('value', item.get('default'))
            merged[key] = persisted.get(key, default)
    else:
        merged = persisted

    return {
        'declared': declared,
        'values': merged,
    }


@router.post("/{module_id}/configurables")
async def save_module_configurables(module_id: str, payload: dict, db: AsyncSession = Depends(get_db)):
    """Persist module configurable key/value pairs. Upserts per module.

    Currently stores company-agnostic values. Payload expected to be { key: value, ... }
    """
    if module_id not in _module_configs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Module '{module_id}' not found")

    try:
        # Upsert each key
        for key, value in payload.items():
            stmt = select(ModuleSetting).where(ModuleSetting.module_id == module_id, ModuleSetting.key == key)
            res = await db.execute(stmt)
            row = res.scalar_one_or_none()
            if row:
                row.value = value
            else:
                new = ModuleSetting(module_id=module_id, key=key, value=value)
                db.add(new)

        await db.commit()
        return {"status": "ok"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/{module_id}/fix")
async def fix_module_schema(module_id: str):
    """Attempt to run module-provided fix/initialization. Looks for a module `setup.py` with `fix()` or `initialize()`.

    This is intentionally generic: modules can provide a `fix` function to perform DB migrations, seed data, or reinit steps.
    """
    if module_id not in _module_configs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Module '{module_id}' not found")

    # Try importing tera.modules.<module_id>.setup
    try:
        module_path = f"tera.modules.{module_id}.setup"
        mod = importlib.import_module(module_path)
    except ModuleNotFoundError as exc:
        raise HTTPException(status_code=501, detail="Module does not implement a setup.fix or setup.initialize function") from exc

    # Prefer async/sync fix or initialize
    func = None
    for name in ("fix", "initialize", "initialize_module"):
        if hasattr(mod, name) and inspect.isfunction(getattr(mod, name)):
            func = getattr(mod, name)
            break

    if not func:
        raise HTTPException(status_code=501, detail="Module setup module does not export a 'fix' or 'initialize' function")

    try:
        result = func()
        # If coroutine, await it
        if inspect.isawaitable(result):
            await result

        return {"status": "ok", "message": "Module fix executed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Module fix failed: {str(e)}") from e


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


@router.get("/{module_id}/status")
async def get_module_status(
    module_id: str,
    company_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get the enabled/disabled status of a module"""
    from tera.modules.core.models import ModuleStatus
    
    if module_id not in _module_configs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module '{module_id}' not found"
        )
    
    stmt = select(ModuleStatus).where(ModuleStatus.module_id == module_id)
    if company_id is not None:
        stmt = stmt.where(ModuleStatus.company_id == company_id)
    else:
        stmt = stmt.where(ModuleStatus.company_id.is_(None))
    
    result = await db.execute(stmt)
    status_record = result.scalar_one_or_none()
    
    # If no record exists, module is enabled by default
    enabled = status_record.enabled if status_record else True
    
    return {
        "module_id": module_id,
        "enabled": enabled,
        "company_id": company_id,
        "updated_at": status_record.updated_at.isoformat() if status_record else None
    }


@router.put("/{module_id}/status")
async def update_module_status(
    module_id: str,
    status_update: ModuleStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Enable or disable a module"""
    from tera.modules.core.models import ModuleStatus
    from datetime import datetime
    
    if module_id not in _module_configs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module '{module_id}' not found"
        )
    
    # Check if module is a system module that cannot be disabled
    SYSTEM_MODULES = ['company', 'users', 'core']
    if module_id in SYSTEM_MODULES and not status_update.enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot disable system module '{module_id}'. System modules are required for the application to function."
        )
    
    # Find existing status record
    stmt = select(ModuleStatus).where(ModuleStatus.module_id == module_id)
    if status_update.company_id is not None:
        stmt = stmt.where(ModuleStatus.company_id == status_update.company_id)
    else:
        stmt = stmt.where(ModuleStatus.company_id.is_(None))
    
    result = await db.execute(stmt)
    status_record = result.scalar_one_or_none()
    
    if status_record:
        # Update existing record
        status_record.enabled = status_update.enabled
        status_record.updated_at = datetime.utcnow()
        if status_update.enabled:
            status_record.enabled_at = datetime.utcnow()
        else:
            status_record.disabled_at = datetime.utcnow()
    else:
        # Create new record
        status_record = ModuleStatus(
            module_id=module_id,
            company_id=status_update.company_id,
            enabled=status_update.enabled,
            enabled_at=datetime.utcnow() if status_update.enabled else None,
            disabled_at=datetime.utcnow() if not status_update.enabled else None
        )
        db.add(status_record)
    
    await db.commit()
    await db.refresh(status_record)
    
    return {
        "module_id": module_id,
        "enabled": status_record.enabled,
        "company_id": company_id,
        "updated_at": status_record.updated_at.isoformat()
    }


@router.get("/status/all")
async def get_all_module_statuses(
    company_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get status of all modules"""
    from tera.modules.core.models import ModuleStatus
    
    stmt = select(ModuleStatus)
    if company_id is not None:
        stmt = stmt.where(ModuleStatus.company_id == company_id)
    else:
        stmt = stmt.where(ModuleStatus.company_id.is_(None))
    
    result = await db.execute(stmt)
    status_records = result.scalars().all()
    
    # Build status map
    status_map = {record.module_id: record.enabled for record in status_records}
    
    # Include all registered modules with default enabled=True if not in DB
    all_statuses = []
    for module_id in _module_configs.keys():
        all_statuses.append({
            "module_id": module_id,
            "enabled": status_map.get(module_id, True),
            "company_id": company_id
        })
    
    return all_statuses

