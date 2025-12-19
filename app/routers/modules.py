"""
Modules router - API endpoints for module system
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path
import importlib
import inspect

from app.core.database import get_db
from app.modules.core import ModuleLoader
from app.modules.core.models import ModuleSetting

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

    # Try importing app.modules.<module_id>.setup
    try:
        module_path = f"app.modules.{module_id}.setup"
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
