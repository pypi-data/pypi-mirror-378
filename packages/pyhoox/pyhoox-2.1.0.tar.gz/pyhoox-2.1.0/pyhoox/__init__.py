from typing import Any, Dict, List, Optional, Callable, Union, TypeVar, Generic
import asyncio
import time
from contextlib import contextmanager
from dataclasses import dataclass

from .core.registry import SyncHookRegistry
from .core.async_registry import AsyncHookRegistry
from .core.context import ContextManager, HookNamespace
from .features.middleware import FilterEngine, MiddlewareManager
from .features.decorators import (
    hook, before, after, around, hookable, hook_class,
    conditional_hook, once_hook, priority_hook,
    critical_hook, high_priority_hook, low_priority_hook, background_hook
)
from .features.persistence import PersistenceManager, PicklePersistenceBackend
from .features.monitoring import HookMonitor, DebugHookRegistry
from .features.validation import create_validator, combine_validators
from .types import (
    HookPriority, ExecutionStrategy, HookMetadata, HookExecution,
    HookExecutionResult, HookError, HookValidationError, 
    HookExecutionError, HookRegistrationError, HookNotFoundError
)

T = TypeVar('T')

class PyHook:
    def __init__(self):
        self._sync_registry = SyncHookRegistry()
        self._async_registry = AsyncHookRegistry()
        self._context_manager = ContextManager()
        self._filter_engine = FilterEngine()
        self._middleware_manager = MiddlewareManager()
        self._persistence_manager = PersistenceManager()
        self._monitor = HookMonitor()
        self._namespaces: Dict[str, HookNamespace] = {}
        
    def use(self, name: str, callback: Callable, **options) -> None:
        if asyncio.iscoroutinefunction(callback):
            # Las funciones async van al registro async
            self._async_registry.register(name, callback, **options)
        else:
            # Las funciones sync van al registro sync
            self._sync_registry.register(name, callback, **options)
        self._monitor.on_register(name, callback, **options)
        
    def use_once(self, name: str, callback: Callable, **options) -> None:
        options['once'] = True
        self.use(name, callback, **options)
        
    def use_with_priority(self, name: str, callback: Callable, priority: int, **options) -> None:
        options['priority'] = priority
        self.use(name, callback, **options)
        
    def use_conditional(self, name: str, callback: Callable, condition: Callable[..., bool], **options) -> None:
        options['condition'] = condition
        self.use(name, callback, **options)
        
    def use_with_filter(self, name: str, callback: Callable, filter_func: Callable[[Any], Any], **options) -> None:
        options['filter'] = filter_func
        self.use(name, callback, **options)
        
    def use_with_validator(self, name: str, callback: Callable, validator: Union[Callable[[Any], bool], Dict[str, Any], type], **options) -> None:
        if not callable(validator):
            validator = create_validator(validator)
        options['validator'] = validator
        self.use(name, callback, **options)
        
    def remove(self, name: str, callback: Optional[Callable] = None) -> None:
        try:
            self._sync_registry.unregister(name, callback)
        except:
            pass
        try:
            self._async_registry.unregister(name, callback)
        except:
            pass
        self._monitor.on_unregister(name, callback)
        
    def trigger(self, name: str, *args, **kwargs) -> List[Any]:
        self._monitor.on_trigger(name, args, kwargs)
        strategy = kwargs.pop('_strategy', ExecutionStrategy.SEQUENTIAL)
        
        if name in self._sync_registry._hooks:
            return self._sync_registry.trigger(name, *args, _strategy=strategy, **kwargs)
        return []
        
    async def async_trigger(self, name: str, *args, **kwargs) -> List[Any]:
        self._monitor.on_trigger(name, args, kwargs)
        strategy = kwargs.pop('_strategy', ExecutionStrategy.SEQUENTIAL)
        
        all_results = []
        
        # Ejecutamos hooks async
        if name in self._async_registry._hooks:
            async_results = await self._async_registry.trigger(name, *args, _strategy=strategy, **kwargs)
            all_results.extend(async_results)
        
        # También ejecutamos hooks sync en contexto async
        if name in self._sync_registry._hooks:
            sync_results = self._sync_registry.trigger(name, *args, _strategy=strategy, **kwargs)
            all_results.extend(sync_results)
        
        return all_results
        
    def trigger_with_return(self, name: str, *args, **kwargs) -> List[Any]:
        results = self.trigger(name, *args, **kwargs)
        return [r for r in results if r is not None]
        
    async def async_trigger_with_return(self, name: str, *args, **kwargs) -> List[Any]:
        results = await self.async_trigger(name, *args, **kwargs)
        return [r for r in results if r is not None]
        
    def list_hooks(self, name: Optional[str] = None) -> Dict[str, List[HookMetadata]]:
        sync_hooks = self._sync_registry.list_hooks(name)
        return sync_hooks
        
    def get_hook_count(self, name: Optional[str] = None) -> int:
        return self._sync_registry.get_hook_count(name)
        
    def clear_hooks(self, name: Optional[str] = None) -> None:
        self._sync_registry.clear_hooks(name)
        
    @contextmanager
    def namespace(self, name: str):
        if name not in self._namespaces:
            context = self._context_manager.create_context(name)
            self._namespaces[name] = HookNamespace(name, self._context_manager)
        
        with self._namespaces[name]:
            yield self._namespaces[name]
            
    def create_namespace(self, name: str) -> HookNamespace:
        if name not in self._namespaces:
            context = self._context_manager.create_context(name)
            self._namespaces[name] = HookNamespace(name, self._context_manager)
        return self._namespaces[name]
        
    def add_filter(self, hook_name: str, filter_func: Callable[[Any], Any]) -> None:
        self._filter_engine.add_filter(hook_name, filter_func)
        
    def add_validator(self, hook_name: str, validator: Union[Callable[[Any], bool], Dict[str, Any], type]) -> None:
        if not callable(validator):
            validator = create_validator(validator)
        self._filter_engine.add_validator(hook_name, validator)
        
    def get_stats(self, hook_name: Optional[str] = None):
        return self._monitor.get_stats(hook_name)
        
    def get_execution_history(self, hook_name: Optional[str] = None, limit: Optional[int] = None):
        return self._monitor.get_execution_history(hook_name, limit)
        
    def print_stats(self, hook_name: Optional[str] = None) -> None:
        self._monitor.print_summary(hook_name)
        
    def enable_persistence(self, backend=None, auto_save: bool = True, interval: float = 60.0) -> None:
        if backend:
            self._persistence_manager.backend = backend
        self._persistence_manager.set_auto_save(auto_save, interval)
        
    def save_hooks(self) -> None:
        hooks = self.list_hooks()
        self._persistence_manager.force_save(hooks)
        
    def load_hooks(self) -> None:
        pass
        
    def debug_mode(self, enabled: bool = True) -> None:
        if enabled:
            self._sync_registry = DebugHookRegistry(self._sync_registry, self._monitor)
        
    def get_monitor(self) -> HookMonitor:
        return self._monitor

_global_pyhook = PyHook()

def use(name: str, callback: Callable, **options) -> None:
    _global_pyhook.use(name, callback, **options)

def use_once(name: str, callback: Callable, **options) -> None:
    _global_pyhook.use_once(name, callback, **options)

def remove(name: str, callback: Optional[Callable] = None) -> None:
    _global_pyhook.remove(name, callback)

def trigger(name: str, *args, **kwargs) -> List[Any]:
    return _global_pyhook.trigger(name, *args, **kwargs)

async def async_trigger(name: str, *args, **kwargs) -> List[Any]:
    return await _global_pyhook.async_trigger(name, *args, **kwargs)

def trigger_with_return(name: str, *args, **kwargs) -> List[Any]:
    return _global_pyhook.trigger_with_return(name, *args, **kwargs)

async def async_trigger_with_return(name: str, *args, **kwargs) -> List[Any]:
    return await _global_pyhook.async_trigger_with_return(name, *args, **kwargs)

def list_hooks(name: Optional[str] = None) -> Dict[str, List[HookMetadata]]:
    return _global_pyhook.list_hooks(name)

def clear_hooks(name: Optional[str] = None) -> None:
    _global_pyhook.clear_hooks(name)

def namespace(name: str):
    return _global_pyhook.namespace(name)

def get_stats(hook_name: Optional[str] = None):
    return _global_pyhook.get_stats(hook_name)

def print_stats(hook_name: Optional[str] = None) -> None:
    _global_pyhook.print_stats(hook_name)

def enable_debug() -> None:
    _global_pyhook.debug_mode(True)

def get_global_instance() -> PyHook:
    return _global_pyhook

hooks = _global_pyhook._sync_registry._hooks

__version__ = "2.0.0"

__all__ = [
    "use", "use_once", "remove", "trigger", "async_trigger", "trigger_with_return", "async_trigger_with_return",
    "list_hooks", "clear_hooks", "hooks",
    "hook", "before", "after", "around", "hookable", "hook_class",
    "conditional_hook", "once_hook", "priority_hook",
    "critical_hook", "high_priority_hook", "low_priority_hook", "background_hook",
    "namespace", "get_stats", "print_stats", "enable_debug",
    "create_validator", "combine_validators",
    "PyHook", "HookPriority", "ExecutionStrategy", "HookMetadata", "HookExecution",
    "HookExecutionResult", "HookError", "HookValidationError", 
    "HookExecutionError", "HookRegistrationError", "HookNotFoundError",
    "get_global_instance", "__version__"
]