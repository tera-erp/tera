"""
Module system - Core classes and types for YAML-driven modules
"""
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from pydantic import BaseModel, Field
import yaml
from pathlib import Path


class FieldType(str, Enum):
    TEXT = "text"
    EMAIL = "email"
    NUMBER = "number"
    DECIMAL = "decimal"
    DATE = "date"
    DATETIME = "datetime"
    SELECT = "select"
    CHECKBOX = "checkbox"
    TEXTAREA = "textarea"
    ARRAY = "array"
    RICHTEXT = "richtext"
    FILE = "file"
    RATING = "rating"
    TAGS = "tags"


class FieldSize(str, Enum):
    FULL = "full"
    HALF = "half"
    THIRD = "third"
    TWO_THIRDS = "two-thirds"


class FormFieldConfig(BaseModel):
    """Configuration for a form field"""
    type: FieldType
    label: str
    required: bool = False
    readonly: bool = False
    help_text: Optional[str] = None
    placeholder: Optional[str] = None
    default: Optional[Any] = None
    
    # UI Layout
    size: Optional[FieldSize] = None
    grid_column: Optional[int] = None
    hidden: bool = False
    hidden_if: Optional[str] = None  # JS expression
    disabled_if: Optional[str] = None  # JS expression
    
    # For select/dropdown
    endpoint: Optional[str] = None  # API endpoint for options
    display_field: Optional[str] = None  # Field to display
    value_field: Optional[str] = None  # Field to use as value
    searchable: bool = False
    clearable: bool = False
    options: Optional[List[Dict[str, Any]]] = None  # Inline options: [{value, label}, ...]
    
    # For arrays
    fields: Optional[Dict[str, 'FormFieldConfig']] = None
    min_rows: Optional[int] = None
    max_rows: Optional[int] = None
    
    # Computed fields
    formula: Optional[str] = None  # Client-side calculation
    
    # Validation
    pattern: Optional[str] = None
    min: Optional[Any] = None
    max: Optional[Any] = None
    minLength: Optional[int] = None
    maxLength: Optional[int] = None
    
    class Config:
        use_enum_values = True


class FormLayout(BaseModel):
    """Layout configuration for forms"""
    type: str  # grid, tabs, accordion, wizard
    columns: Optional[int] = None
    gaps: Optional[str] = None  # small, medium, large
    sections: Optional[List[Dict[str, Any]]] = None


class FormConfig(BaseModel):
    """Configuration for a form"""
    title: str
    description: Optional[str] = None
    edit_title: Optional[str] = None
    edit_description: Optional[str] = None
    fields: Dict[str, FormFieldConfig]
    layout: Optional[FormLayout] = None
    submit_label: Optional[str] = None
    edit_submit_label: Optional[str] = None
    cancel_label: Optional[str] = None
    back_button: Optional[Dict[str, Any]] = None  # {enabled, label, navigate_to}
    
    class Config:
        arbitrary_types_allowed = True


class ScreenType(str, Enum):
    LIST = "list"
    DETAIL = "detail"
    FORM = "form"
    DASHBOARD = "dashboard"
    CUSTOM = "custom"


class ListConfig(BaseModel):
    """Configuration for list view"""
    columns: List[str]
    searchable_fields: Optional[List[str]] = None
    sortable: bool = False
    filterable: bool = False
    paginated: bool = False
    page_size: Optional[int] = None
    selectable: bool = False
    row_actions: Optional[List[Dict[str, Any]]] = None


class DetailConfig(BaseModel):
    """Configuration for detail view"""
    form: Optional[str] = None
    show_metadata: Optional[bool] = None
    show_related: Optional[bool] = None
    sidebar: Optional[Dict[str, Any]] = None
    actions: Optional[List[str]] = None
    related_records: Optional[List[Dict[str, Any]]] = None


class ScreenConfig(BaseModel):
    """Configuration for a screen"""
    title: str
    description: Optional[str] = None
    path: str
    type: ScreenType = ScreenType.CUSTOM
    
    # Navigation
    show_in_nav: bool = True
    create_screen: Optional[str] = None  # Screen ID to navigate to for creation (for list screens)
    
    # Data source
    endpoint: Optional[str] = None
    list_endpoint: Optional[str] = None
    detail_endpoint: Optional[str] = None
    
    # Permissions
    permissions: List[str] = Field(default_factory=list)
    
    # List view config
    list_config: Optional[ListConfig] = None
    
    # Detail view config
    detail_config: Optional[DetailConfig] = None
    
    # Responsive
    layout: Optional[str] = None
    mobile_hidden: bool = False
    
    class Config:
        use_enum_values = True


class WorkflowState(BaseModel):
    """Configuration for a workflow state"""
    label: str
    color: Optional[str] = None
    can_transition_to: List[str] = Field(default_factory=list)
    allow_edit: bool = True
    allow_delete: bool = False
    
    class Config:
        use_enum_values = True


class WorkflowTransition(BaseModel):
    """Configuration for a workflow transition"""
    from_state: str = Field(alias='from')
    to_state: str = Field(alias='to')
    label: str
    action: str
    confirm_message: Optional[str] = None
    disabled_if: Optional[str] = None  # Expression to evaluate
    permissions: List[str] = Field(default_factory=list)
    
    class Config:
        populate_by_name = True


class WorkflowConfig(BaseModel):
    """Configuration for a workflow"""
    title: str
    initial_state: str
    states: Dict[str, WorkflowState]
    transitions: Optional[Dict[str, WorkflowTransition]] = None


class ActionConfig(BaseModel):
    """Configuration for an action"""
    type: str  # 'api', 'custom', 'batch'
    method: Optional[str] = None  # HTTP method
    endpoint: Optional[str] = None  # API endpoint
    handler: Optional[str] = None  # Custom handler function name
    success_message: Optional[str] = None
    error_message: Optional[str] = None
    on_success: Optional[List[Dict[str, Any]]] = None


class ModuleConfig(BaseModel):
    """Full module configuration from YAML"""
    module: Dict[str, Any]  # id, name, version, description, author, icon, color
    screens: Optional[Dict[str, ScreenConfig]] = None
    forms: Optional[Dict[str, FormConfig]] = None
    workflows: Optional[Dict[str, WorkflowConfig]] = None
    actions: Optional[Dict[str, ActionConfig]] = None
    permissions: List[str] = Field(default_factory=list)
    menu: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        arbitrary_types_allowed = True


class ModuleLoader:
    """Loads and parses module YAML configurations"""
    
    @staticmethod
    def _deep_merge(base: dict, overlay: dict) -> dict:
        """Deep merge two dictionaries, with overlay taking precedence"""
        result = base.copy()
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ModuleLoader._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    @staticmethod
    def load(module_path: Path) -> ModuleConfig:
        """Load module config from YAML file(s).

        Supports two patterns:
        1. Single config.yaml file
        2. Multiple YAML files in configs/ directory (merged in alphabetical order)
        """
        config_file = module_path / "config.yaml"
        configs_dir = module_path / "configs"  #? Is this a security concern?

        # Start with base config
        if not config_file.exists() and not configs_dir.exists():
            raise FileNotFoundError(f"Module config not found: {config_file} or {configs_dir}")

        data = {}
        
        # Load main config.yaml if it exists
        if config_file.exists():
            with open(config_file, 'r') as f:
                data = yaml.safe_load(f) or {}
        
        # Load and merge configs from configs/ directory
        if configs_dir.exists() and configs_dir.is_dir():
            yaml_files = sorted(configs_dir.glob("*.yaml"))
            for yaml_file in yaml_files:
                with open(yaml_file, 'r') as f:
                    overlay = yaml.safe_load(f) or {}
                    data = ModuleLoader._deep_merge(data, overlay)
        
        # Parse and validate
        return ModuleConfig(**data)
    
    @staticmethod
    def load_all(modules_dir: Path) -> Dict[str, ModuleConfig]:
        """Load all modules from modules directory"""
        modules = {}
        
        if not modules_dir.exists():
            return modules
        
        # Skip core and special directories
        skip_dirs = {'.', '__pycache__', 'core', '__init__.py'}
        
        for module_dir in modules_dir.iterdir():
            # Skip non-directories and special directories
            if not module_dir.is_dir():
                continue
            if module_dir.name in skip_dirs or module_dir.name.startswith('_'):
                continue
            
            try:
                config = ModuleLoader.load(module_dir)
                module_id = config.module.get('id')
                if module_id:
                    modules[module_id] = config
            except FileNotFoundError:
                # Directory doesn't have config.yaml, skip it
                pass
            except Exception as e:
                print(f"Failed to load module {module_dir.name}: {e}")
        
        return modules


class WorkflowState:
    """Workflow state machine"""
    
    def __init__(self, config: WorkflowConfig):
        self.config = config
        self.current_state = config.initial_state
    
    def can_transition_to(self, next_state: str) -> bool:
        """Check if transition is allowed from current state"""
        state_config = self.config.states.get(self.current_state)
        if not state_config:
            return False
        return next_state in state_config.can_transition_to
    
    def transition(self, next_state: str) -> bool:
        """Transition to next state"""
        if self.can_transition_to(next_state):
            self.current_state = next_state
            return True
        return False
    
    def get_current_state_config(self) -> Optional[WorkflowState]:
        """Get config for current state"""
        return self.config.states.get(self.current_state)
    
    def can_edit(self) -> bool:
        """Check if editing is allowed in current state"""
        state_config = self.get_current_state_config()
        return state_config.allow_edit if state_config else False
    
    def can_delete(self) -> bool:
        """Check if deletion is allowed in current state"""
        state_config = self.get_current_state_config()
        return state_config.allow_delete if state_config else False
