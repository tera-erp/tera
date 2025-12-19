"""
Dynamic module registration system.

This module provides automatic discovery and registration of:
- SQLAlchemy models
- FastAPI routers
- Module actions
- Module configurations
"""
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import importlib
import inspect
from fastapi import APIRouter
from sqlalchemy.orm import DeclarativeMeta

from tera.core.database import Base
from .action import ActionRegistry
from .module import ModuleLoader, ModuleConfig


class ModuleRegistry:
    """Central registry for all module components"""
    
    def __init__(self):
        self._models: Dict[str, List[DeclarativeMeta]] = {}
        self._routers: Dict[str, APIRouter] = {}
        self._configs: Dict[str, ModuleConfig] = {}
        self._initialized = False
    
    def discover_modules(self, modules_dir: Path) -> List[str]:
        """
        Discover all available modules in the modules directory.
        
        Returns:
            List of module names (directory names)
        """
        if not modules_dir.exists():
            return []
        
        skip_dirs = {'core', '__pycache__', '.'}
        modules = []
        
        for module_dir in modules_dir.iterdir():
            if not module_dir.is_dir():
                continue
            if module_dir.name in skip_dirs or module_dir.name.startswith('_'):
                continue
            modules.append(module_dir.name)
        
        return sorted(modules)
    
    def register_models(self, module_name: str, models_module: Any) -> None:
        """
        Register SQLAlchemy models from a module.
        
        Args:
            module_name: Name of the module (e.g., 'finance', 'payroll')
            models_module: Imported models module
        """
        models = []
        
        for name, obj in inspect.getmembers(models_module):
            # Check if it's a SQLAlchemy model class
            if (inspect.isclass(obj) and 
                hasattr(obj, '__tablename__') and 
                isinstance(obj, type) and 
                issubclass(obj, Base) and 
                obj is not Base):
                models.append(obj)
        
        if models:
            self._models[module_name] = models
            print(f"  ✓ Registered {len(models)} model(s) from {module_name}")
    
    def register_router(self, module_name: str, router: APIRouter) -> None:
        """
        Register a FastAPI router for a module.
        
        Args:
            module_name: Name of the module
            router: FastAPI APIRouter instance
        """
        self._routers[module_name] = router
        print(f"  ✓ Registered router for {module_name}")
    
    def register_config(self, module_name: str, config: ModuleConfig) -> None:
        """
        Register module configuration.
        
        Args:
            module_name: Name of the module
            config: ModuleConfig instance
        """
        self._configs[module_name] = config
    
    def register_actions(self, module_name: str, actions: Dict[str, Callable]) -> None:
        """
        Register module actions with the ActionRegistry.
        
        Args:
            module_name: Name of the module
            actions: Dictionary of action name -> action function
        """
        ActionRegistry.register_module_actions(module_name, actions)
        print(f"  ✓ Registered {len(actions)} action(s) for {module_name}")
    
    def load_module(self, module_name: str, modules_dir: Path) -> None:
        """
        Load a single module and register all its components.
        
        This method attempts to:
        1. Import and register models (if models.py exists)
        2. Import and register router (if router.py exists)
        3. Load and register config (if config.yaml exists)
        4. Call register_actions() if defined in __init__.py
        
        Args:
            module_name: Name of the module directory
            modules_dir: Path to modules directory
        """
        module_path = modules_dir / module_name
        module_import_path = f"tera.modules.{module_name}"
        
        print(f"Loading module: {module_name}")
        
        # 1. Register models
        try:
            models_module = importlib.import_module(f"{module_import_path}.models")
            self.register_models(module_name, models_module)
        except ModuleNotFoundError:
            pass  # Module doesn't have models
        except Exception as e:
            print(f"  ⚠ Failed to load models from {module_name}: {e}")
        
        # 2. Register router
        try:
            router_module = importlib.import_module(f"{module_import_path}.router")
            if hasattr(router_module, 'router'):
                self.register_router(module_name, router_module.router)
        except ModuleNotFoundError:
            pass  # Module doesn't have router
        except Exception as e:
            print(f"  ⚠ Failed to load router from {module_name}: {e}")
        
        # 3. Load configuration
        try:
            config = ModuleLoader.load(module_path)
            self.register_config(module_name, config)
            print(f"  ✓ Loaded config for {module_name}")
        except FileNotFoundError:
            pass  # Module doesn't have config
        except Exception as e:
            print(f"  ⚠ Failed to load config for {module_name}: {e}")
        
        # 4. Register actions (if register_actions function exists)
        try:
            module_init = importlib.import_module(module_import_path)
            if hasattr(module_init, 'register_actions'):
                module_init.register_actions()
        except ModuleNotFoundError:
            pass
        except Exception as e:
            print(f"  ⚠ Failed to register actions for {module_name}: {e}")
    
    def initialize(self, modules_dir: Path) -> None:
        """
        Initialize the module registry by discovering and loading all modules.
        
        Args:
            modules_dir: Path to the modules directory
        """
        if self._initialized:
            print("Module registry already initialized")
            return
        
        print("=" * 60)
        print("Initializing Module Registry")
        print("=" * 60)
        
        modules = self.discover_modules(modules_dir)
        print(f"Discovered {len(modules)} module(s): {', '.join(modules)}")
        print()
        
        for module_name in modules:
            try:
                self.load_module(module_name, modules_dir)
            except Exception as e:
                print(f"⚠ Failed to load module {module_name}: {e}")
            print()
        
        self._initialized = True
        
        print("=" * 60)
        print(f"Module Registry Initialized:")
        print(f"  • {len(self._models)} module(s) with models")
        print(f"  • {len(self._routers)} module(s) with routers")
        print(f"  • {len(self._configs)} module(s) with configs")
        print(f"  • {len(ActionRegistry._handlers)} total action(s) registered")
        print("=" * 60)
    
    def get_models(self, module_name: Optional[str] = None) -> Dict[str, List[DeclarativeMeta]]:
        """Get registered models, optionally filtered by module"""
        if module_name:
            return {module_name: self._models.get(module_name, [])}
        return self._models
    
    def get_routers(self) -> Dict[str, APIRouter]:
        """Get all registered routers"""
        return self._routers
    
    def get_configs(self) -> Dict[str, ModuleConfig]:
        """Get all registered module configs"""
        return self._configs
    
    def get_config(self, module_name: str) -> Optional[ModuleConfig]:
        """Get config for a specific module"""
        return self._configs.get(module_name)
    
    def is_module_enabled(self, module_name: str, company_id: Optional[int] = None) -> bool:
        """Check if a module is enabled (defaults to True if not explicitly disabled)"""
        # If module doesn't exist in registry, it's not available
        if module_name not in self._configs:
            return False
        
        # Import here to avoid circular dependency
        from tera.modules.core.models import ModuleStatus
        from sqlalchemy import select
        from tera.core.database import SessionLocal
        
        try:
            with SessionLocal() as db:
                stmt = select(ModuleStatus).where(
                    ModuleStatus.module_id == module_name
                )
                if company_id is not None:
                    stmt = stmt.where(ModuleStatus.company_id == company_id)
                else:
                    stmt = stmt.where(ModuleStatus.company_id.is_(None))
                
                result = db.execute(stmt)
                status = result.scalar_one_or_none()
                
                # If no status record exists, module is enabled by default
                if status is None:
                    return True
                
                return status.enabled
        except Exception as e:
            print(f"Error checking module status: {e}")
            # Default to enabled if there's an error
            return True


# Global registry instance
registry = ModuleRegistry()
