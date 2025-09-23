from typing import Any, Dict, List, Optional, Callable, Set, cast
from abc import ABC, abstractmethod
import time
import asyncio
import weakref
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..types import (
    HookMetadata, HookExecution, HookExecutionResult, 
    ExecutionStrategy, HookPriority, HookCallback, 
    AsyncHookCallback, HookError, HookExecutionError, 
    HookRegistrationError, HookNotFoundError, ConditionFunction, ValidatorFunction
)

class BaseHookRegistry(ABC):
    def __init__(self):
        self._hooks: Dict[str, List[HookMetadata]] = {}
        self._execution_history: List[HookExecution] = []
        self._max_history: int = 1000
        
    @abstractmethod
    def register(self, name: str, callback: Callable, **options) -> None:
        pass
        
    @abstractmethod
    def unregister(self, name: str, callback: Optional[Callable] = None) -> None:
        pass
        
    @abstractmethod
    def trigger(self, name: str, *args, **kwargs) -> Any:
        pass
        
    def list_hooks(self, name: Optional[str] = None) -> Dict[str, List[HookMetadata]]:
        if name:
            return {name: self._hooks.get(name, [])}
        return self._hooks.copy()
        
    def get_hook_count(self, name: Optional[str] = None) -> int:
        if name:
            return len(self._hooks.get(name, []))
        return sum(len(hooks) for hooks in self._hooks.values())
        
    def clear_hooks(self, name: Optional[str] = None) -> None:
        if name:
            self._hooks.pop(name, None)
        else:
            self._hooks.clear()
            
    def get_execution_history(self, limit: Optional[int] = None) -> List[HookExecution]:
        if limit:
            return self._execution_history[-limit:]
        return self._execution_history.copy()
        
    def clear_history(self) -> None:
        self._execution_history.clear()
        
    def _add_to_history(self, execution: HookExecution) -> None:
        self._execution_history.append(execution)
        if len(self._execution_history) > self._max_history:
            self._execution_history = self._execution_history[-self._max_history:]

class SyncHookRegistry(BaseHookRegistry):
    def __init__(self, default_strategy: ExecutionStrategy = ExecutionStrategy.SEQUENTIAL):
        super().__init__()
        self._default_strategy = default_strategy
        self._thread_pool: Optional[ThreadPoolExecutor] = None
        
    def register(self, name: str, callback: HookCallback, **options) -> None:
        if not callable(callback):
            raise HookRegistrationError(f"Callback must be callable, got {type(callback)}")
            
        priority = options.get('priority', HookPriority.NORMAL)
        once = options.get('once', False)
        condition = options.get('condition')
        filter_func = options.get('filter')
        validator = options.get('validator')
        context = options.get('context')
        tags = options.get('tags', [])
        
        if condition and not callable(condition):
            raise HookRegistrationError("Condition must be callable")
        if filter_func and not callable(filter_func):
            raise HookRegistrationError("Filter must be callable") 
        if validator and not callable(validator):
            raise HookRegistrationError("Validator must be callable")
            
        condition_func = cast(Optional[ConditionFunction], condition)
        validator_func = cast(Optional[ValidatorFunction], validator)
            
        hook_meta = HookMetadata(
            name=name,
            callback=callback,
            priority=priority,
            once=once,
            condition=condition_func,
            filter_func=filter_func,
            validator=validator_func,
            context=context,
            tags=tags,
            created_at=time.time()
        )
        
        if name not in self._hooks:
            self._hooks[name] = []
            
        self._hooks[name].append(hook_meta)
        self._hooks[name].sort(key=lambda h: h.priority)
        
    def unregister(self, name: str, callback: Optional[HookCallback] = None) -> None:
        if name not in self._hooks:
            raise HookNotFoundError(f"Hook '{name}' not found")
            
        if callback is None:
            del self._hooks[name]
        else:
            original_count = len(self._hooks[name])
            self._hooks[name] = [h for h in self._hooks[name] if h.callback != callback]
            
            if len(self._hooks[name]) == original_count:
                raise HookNotFoundError(f"Callback not found for hook '{name}'")
                
            if not self._hooks[name]:
                del self._hooks[name]
                
    def trigger(self, name: str, *args, **kwargs) -> List[Any]:
        if name not in self._hooks:
            return []
            
        strategy = kwargs.pop('_strategy', self._default_strategy)
        return self._execute_hooks(name, args, kwargs, strategy)
        
    def _execute_hooks(self, name: str, args: tuple, kwargs: dict, strategy: ExecutionStrategy) -> List[Any]:
        hooks = self._hooks[name].copy()
        results = []
        executions = []
        
        if strategy == ExecutionStrategy.PARALLEL:
            results = self._execute_parallel(hooks, name, args, kwargs)
        elif strategy == ExecutionStrategy.FAIL_FAST:
            results = self._execute_fail_fast(hooks, name, args, kwargs)
        elif strategy == ExecutionStrategy.IGNORE_ERRORS:
            results = self._execute_ignore_errors(hooks, name, args, kwargs)
        else:
            results = self._execute_sequential(hooks, name, args, kwargs)
            
        self._cleanup_once_hooks(name)
        return results
        
    def _execute_sequential(self, hooks: List[HookMetadata], name: str, args: tuple, kwargs: dict) -> List[Any]:
        results = []
        
        for hook in hooks:
            try:
                result = self._execute_single_hook(hook, args, kwargs)
                if result is not None:
                    results.append(result)
            except Exception as e:
                execution = HookExecution(
                    hook_name=name,
                    callback=hook.callback,
                    args=args,
                    kwargs=kwargs,
                    error=e,
                    status=HookExecutionResult.FAILED
                )
                self._add_to_history(execution)
                raise HookExecutionError(f"Hook '{name}' failed: {e}") from e
                
        return results
        
    def _execute_parallel(self, hooks: List[HookMetadata], name: str, args: tuple, kwargs: dict) -> List[Any]:
        if not self._thread_pool:
            self._thread_pool = ThreadPoolExecutor(max_workers=4)
            
        futures = []
        for hook in hooks:
            future = self._thread_pool.submit(self._execute_single_hook, hook, args, kwargs)
            futures.append(future)
            
        results = []
        for future in as_completed(futures):
            try:
                result = future.result()
                if result is not None:
                    results.append(result)
            except Exception as e:
                raise HookExecutionError(f"Parallel hook execution failed: {e}") from e
                
        return results
        
    def _execute_fail_fast(self, hooks: List[HookMetadata], name: str, args: tuple, kwargs: dict) -> List[Any]:
        results = []
        
        for hook in hooks:
            try:
                result = self._execute_single_hook(hook, args, kwargs)
                if result is not None:
                    results.append(result)
            except Exception as e:
                execution = HookExecution(
                    hook_name=name,
                    callback=hook.callback,
                    args=args,
                    kwargs=kwargs,
                    error=e,
                    status=HookExecutionResult.FAILED
                )
                self._add_to_history(execution)
                return results
                
        return results
        
    def _execute_ignore_errors(self, hooks: List[HookMetadata], name: str, args: tuple, kwargs: dict) -> List[Any]:
        results = []
        
        for hook in hooks:
            try:
                result = self._execute_single_hook(hook, args, kwargs)
                if result is not None:
                    results.append(result)
            except Exception as e:
                execution = HookExecution(
                    hook_name=name,
                    callback=hook.callback,
                    args=args,
                    kwargs=kwargs,
                    error=e,
                    status=HookExecutionResult.FAILED
                )
                self._add_to_history(execution)
                continue
                
        return results
        
    def _execute_single_hook(self, hook: HookMetadata, args: tuple, kwargs: dict) -> Any:
        start_time = time.time()
        
        if hook.condition and not hook.condition(*args, **kwargs):
            execution = HookExecution(
                hook_name=hook.name,
                callback=hook.callback,
                args=args,
                kwargs=kwargs,
                status=HookExecutionResult.FILTERED,
                execution_time=time.time() - start_time
            )
            self._add_to_history(execution)
            return None
            
        processed_args = args
        if hook.filter_func:
            try:
                if args:
                    processed_args = (hook.filter_func(args[0]),) + args[1:]
            except Exception as e:
                raise HookExecutionError(f"Filter function failed: {e}") from e
                
        if hook.validator:
            try:
                if not hook.validator(processed_args[0] if processed_args else None):
                    execution = HookExecution(
                        hook_name=hook.name,
                        callback=hook.callback,
                        args=args,
                        kwargs=kwargs,
                        status=HookExecutionResult.FILTERED,
                        execution_time=time.time() - start_time
                    )
                    self._add_to_history(execution)
                    return None
            except Exception as e:
                raise HookExecutionError(f"Validation failed: {e}") from e
                
        try:
            result = hook.callback(*processed_args, **kwargs)
            hook.call_count += 1
            
            execution = HookExecution(
                hook_name=hook.name,
                callback=hook.callback,
                args=processed_args,
                kwargs=kwargs,
                result=result,
                status=HookExecutionResult.SUCCESS,
                execution_time=time.time() - start_time
            )
            self._add_to_history(execution)
            
            return result
            
        except Exception as e:
            execution = HookExecution(
                hook_name=hook.name,
                callback=hook.callback,
                args=processed_args,
                kwargs=kwargs,
                error=e,
                status=HookExecutionResult.FAILED,
                execution_time=time.time() - start_time
            )
            self._add_to_history(execution)
            raise
            
    def _cleanup_once_hooks(self, name: str) -> None:
        if name in self._hooks:
            self._hooks[name] = [h for h in self._hooks[name] if not h.once]
            if not self._hooks[name]:
                del self._hooks[name]
                
    def __del__(self):
        if self._thread_pool:
            self._thread_pool.shutdown(wait=False)
