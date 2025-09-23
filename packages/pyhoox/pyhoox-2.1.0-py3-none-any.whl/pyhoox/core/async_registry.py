from typing import Any, Dict, List, Optional, Callable, Awaitable, cast
import asyncio
import time
from concurrent.futures import as_completed

from ..types import (
    HookMetadata, HookExecution, HookExecutionResult, 
    ExecutionStrategy, HookPriority, AsyncHookCallback, 
    HookError, HookExecutionError, HookRegistrationError, HookNotFoundError,
    ConditionFunction, ValidatorFunction
)
from .registry import BaseHookRegistry

class AsyncHookRegistry(BaseHookRegistry):
    def __init__(self, default_strategy: ExecutionStrategy = ExecutionStrategy.SEQUENTIAL):
        super().__init__()
        self._default_strategy = default_strategy
        
    def register(self, name: str, callback: AsyncHookCallback, **options) -> None:
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
        
    def unregister(self, name: str, callback: Optional[AsyncHookCallback] = None) -> None:
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
                
    async def trigger(self, name: str, *args, **kwargs) -> List[Any]:
        if name not in self._hooks:
            return []
            
        strategy = kwargs.pop('_strategy', self._default_strategy)
        return await self._execute_hooks(name, args, kwargs, strategy)
        
    async def _execute_hooks(self, name: str, args: tuple, kwargs: dict, strategy: ExecutionStrategy) -> List[Any]:
        hooks = self._hooks[name].copy()
        
        if strategy == ExecutionStrategy.PARALLEL:
            results = await self._execute_parallel(hooks, name, args, kwargs)
        elif strategy == ExecutionStrategy.FAIL_FAST:
            results = await self._execute_fail_fast(hooks, name, args, kwargs)
        elif strategy == ExecutionStrategy.IGNORE_ERRORS:
            results = await self._execute_ignore_errors(hooks, name, args, kwargs)
        else:
            results = await self._execute_sequential(hooks, name, args, kwargs)
            
        await self._cleanup_once_hooks(name)
        return results
        
    async def _execute_sequential(self, hooks: List[HookMetadata], name: str, args: tuple, kwargs: dict) -> List[Any]:
        results = []
        
        for hook in hooks:
            try:
                result = await self._execute_single_hook(hook, args, kwargs)
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
        
    async def _execute_parallel(self, hooks: List[HookMetadata], name: str, args: tuple, kwargs: dict) -> List[Any]:
        tasks = []
        for hook in hooks:
            task = asyncio.create_task(self._execute_single_hook(hook, args, kwargs))
            tasks.append(task)
            
        results = []
        try:
            completed_results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in completed_results:
                if isinstance(result, Exception):
                    raise HookExecutionError(f"Parallel hook execution failed: {result}") from result
                elif result is not None:
                    results.append(result)
        except Exception as e:
            for task in tasks:
                if not task.done():
                    task.cancel()
            raise
                
        return results
        
    async def _execute_fail_fast(self, hooks: List[HookMetadata], name: str, args: tuple, kwargs: dict) -> List[Any]:
        results = []
        
        for hook in hooks:
            try:
                result = await self._execute_single_hook(hook, args, kwargs)
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
        
    async def _execute_ignore_errors(self, hooks: List[HookMetadata], name: str, args: tuple, kwargs: dict) -> List[Any]:
        results = []
        
        for hook in hooks:
            try:
                result = await self._execute_single_hook(hook, args, kwargs)
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
        
    async def _execute_single_hook(self, hook: HookMetadata, args: tuple, kwargs: dict) -> Any:
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
            if asyncio.iscoroutinefunction(hook.callback):
                result = await hook.callback(*processed_args, **kwargs)
            else:
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
            
    async def _cleanup_once_hooks(self, name: str) -> None:
        if name in self._hooks:
            self._hooks[name] = [h for h in self._hooks[name] if not h.once]
            if not self._hooks[name]:
                del self._hooks[name]
