from typing import Any, Callable, Dict, List, Optional, Type, Union
from functools import wraps
import inspect
import asyncio

from ..core.registry import SyncHookRegistry
from ..core.async_registry import AsyncHookRegistry
from ..types import HookPriority, ExecutionStrategy

_global_sync_registry = SyncHookRegistry()
_global_async_registry = AsyncHookRegistry()

def hook(
    name: str, 
    *,
    priority: int = HookPriority.NORMAL,
    once: bool = False,
    condition: Optional[Callable[..., bool]] = None,
    filter_func: Optional[Callable[[Any], Any]] = None,
    validator: Optional[Callable[[Any], bool]] = None,
    tags: Optional[List[str]] = None,
    registry: Optional[Union[SyncHookRegistry, AsyncHookRegistry]] = None
):
    def decorator(func: Callable) -> Callable:
        target_registry = registry or (_global_async_registry if asyncio.iscoroutinefunction(func) else _global_sync_registry)
        
        if asyncio.iscoroutinefunction(func):
            asyncio.create_task(target_registry.register(
                name, func, 
                priority=priority, once=once, condition=condition,
                filter=filter_func, validator=validator, tags=tags or []
            ))
        else:
            target_registry.register(
                name, func,
                priority=priority, once=once, condition=condition, 
                filter=filter_func, validator=validator, tags=tags or []
            )
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
            
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
            
        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper
    return decorator

def before(hook_name: str, **options):
    def decorator(func: Callable) -> Callable:
        before_hook_name = f"before_{hook_name}"
        return hook(before_hook_name, **options)(func)
    return decorator

def after(hook_name: str, **options):
    def decorator(func: Callable) -> Callable:
        after_hook_name = f"after_{hook_name}"
        return hook(after_hook_name, **options)(func)
    return decorator

def around(hook_name: str, **options):
    def decorator(func: Callable) -> Callable:
        before_name = f"before_{hook_name}"
        after_name = f"after_{hook_name}"
        
        hook(before_name, **options)(func)
        hook(after_name, **options)(func)
        
        return func
    return decorator

def hookable(
    before_hooks: Optional[List[str]] = None,
    after_hooks: Optional[List[str]] = None,
    strategy: ExecutionStrategy = ExecutionStrategy.SEQUENTIAL,
    registry: Optional[Union[SyncHookRegistry, AsyncHookRegistry]] = None
):
    def decorator(func: Callable) -> Callable:
        func_name = func.__name__
        before_list = before_hooks or [f"before_{func_name}"]
        after_list = after_hooks or [f"after_{func_name}"]
        
        target_registry = registry or (_global_async_registry if asyncio.iscoroutinefunction(func) else _global_sync_registry)
        
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                for hook_name in before_list:
                    await target_registry.trigger(hook_name, *args, **kwargs, _strategy=strategy)
                
                result = await func(*args, **kwargs)
                
                for hook_name in after_list:
                    await target_registry.trigger(hook_name, result, *args, **kwargs, _strategy=strategy)
                
                return result
            return async_wrapper
        else:
            @wraps(func)
            def wrapper(*args, **kwargs):
                for hook_name in before_list:
                    target_registry.trigger(hook_name, *args, **kwargs, _strategy=strategy)
                
                result = func(*args, **kwargs)
                
                for hook_name in after_list:
                    target_registry.trigger(hook_name, result, *args, **kwargs, _strategy=strategy)
                
                return result
            return wrapper
    return decorator

def hook_class(*hook_names: str, **options):
    def decorator(cls: Type) -> Type:
        original_init = cls.__init__
        
        @wraps(original_init)
        def new_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            
            for method_name in dir(self):
                if not method_name.startswith('_'):
                    method = getattr(self, method_name)
                    if callable(method):
                        for hook_name in hook_names:
                            full_hook_name = f"{cls.__name__}_{method_name}_{hook_name}"
                            hook(full_hook_name, **options)(method)
        
        cls.__init__ = new_init
        return cls
    return decorator

def conditional_hook(condition: Callable[..., bool]):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if condition(*args, **kwargs):
                return func(*args, **kwargs)
            return None
            
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if condition(*args, **kwargs):
                return await func(*args, **kwargs)
            return None
            
        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper
    return decorator

def once_hook(name: str, **options):
    options['once'] = True
    return hook(name, **options)

def priority_hook(name: str, priority_level: int, **options):
    options['priority'] = priority_level
    return hook(name, **options)

def critical_hook(name: str, **options):
    return priority_hook(name, HookPriority.CRITICAL, **options)

def high_priority_hook(name: str, **options):
    return priority_hook(name, HookPriority.HIGH, **options)

def low_priority_hook(name: str, **options):
    return priority_hook(name, HookPriority.LOW, **options)

def background_hook(name: str, **options):
    return priority_hook(name, HookPriority.BACKGROUND, **options)
