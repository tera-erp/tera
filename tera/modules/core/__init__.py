"""
Module system core - initialization
"""
from .module import ModuleLoader, ModuleConfig, WorkflowState as WorkflowStateMachine
from .action import ActionRegistry, ActionContext, ActionResult
from .document_engine import DocumentEngine, DocumentFormat, DocumentData, PartyData, LineItemData
from .registry import ModuleRegistry, registry

SYSTEM_MODULES = ['company', 'users', 'core']

__all__ = [
    "ModuleLoader",
    "ModuleConfig", 
    "WorkflowStateMachine",
    "ActionRegistry",
    "ActionContext",
    "ActionResult",
    "DocumentEngine",
    "DocumentFormat",
    "DocumentData",
    "PartyData",
    "LineItemData",
    "ModuleRegistry",
    "registry",
]
