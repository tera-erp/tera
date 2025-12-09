"""
Module system - Action handlers for workflows
"""
from typing import Any, Dict, Optional, Callable
from pydantic import BaseModel


class ActionContext(BaseModel):
    """Context passed to action handlers"""
    user_id: int
    company_id: int
    data: Dict[str, Any]  # Request payload
    metadata: Dict[str, Any] = {}  # Additional context


class ActionResult(BaseModel):
    """Result returned from action handlers"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    redirect_to: Optional[str] = None


class ActionRegistry:
    """Registry for custom action handlers"""
    
    _handlers: Dict[str, Callable] = {}
    
    @classmethod
    def register(cls, name: str, handler: Callable) -> None:
        """Register a custom action handler"""
        cls._handlers[name] = handler
    
    @classmethod
    def get(cls, name: str) -> Optional[Callable]:
        """Get a registered action handler"""
        return cls._handlers.get(name)
    
    @classmethod
    def register_module_actions(cls, module_id: str, actions: Dict[str, Callable]) -> None:
        """Register all actions for a module"""
        for action_name, handler in actions.items():
            full_name = f"{module_id}.{action_name}"
            cls.register(full_name, handler)


async def execute_action(
    action_name: str,
    context: ActionContext,
    registry: ActionRegistry
) -> ActionResult:
    """Execute an action handler"""
    handler = registry.get(action_name)
    
    if not handler:
        return ActionResult(
            success=False,
            message=f"Action '{action_name}' not found"
        )
    
    try:
        result = await handler(context)
        return result
    except Exception as e:
        return ActionResult(
            success=False,
            message=f"Action failed: {str(e)}"
        )
