from typing import Any, Callable, List, Optional, Dict
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..types import HookMiddleware, DataTransformer, HookValidator

@dataclass
class MiddlewareChain:
    pre_middlewares: List[HookMiddleware]
    post_middlewares: List[HookMiddleware]
    transformers: List[DataTransformer]
    validators: List[HookValidator]

class FilterEngine:
    def __init__(self):
        self._filters: Dict[str, List[Callable[[Any], Any]]] = {}
        self._transformers: Dict[str, List[DataTransformer]] = {}
        self._validators: Dict[str, List[HookValidator]] = {}
        
    def add_filter(self, hook_name: str, filter_func: Callable[[Any], Any]) -> None:
        if hook_name not in self._filters:
            self._filters[hook_name] = []
        self._filters[hook_name].append(filter_func)
        
    def add_transformer(self, hook_name: str, transformer: DataTransformer) -> None:
        if hook_name not in self._transformers:
            self._transformers[hook_name] = []
        self._transformers[hook_name].append(transformer)
        
    def add_validator(self, hook_name: str, validator: HookValidator) -> None:
        if hook_name not in self._validators:
            self._validators[hook_name] = []
        self._validators[hook_name].append(validator)
        
    def process_data(self, hook_name: str, data: Any) -> Any:
        processed_data = data
        
        for filter_func in self._filters.get(hook_name, []):
            processed_data = filter_func(processed_data)
            
        for transformer in self._transformers.get(hook_name, []):
            processed_data = transformer.transform(processed_data)
            
        return processed_data
        
    def validate_data(self, hook_name: str, data: Any) -> tuple[bool, Optional[str]]:
        for validator in self._validators.get(hook_name, []):
            if not validator.validate(data):
                return False, validator.get_error_message()
        return True, None
        
    def remove_filter(self, hook_name: str, filter_func: Optional[Callable] = None) -> None:
        if hook_name in self._filters:
            if filter_func is None:
                del self._filters[hook_name]
            else:
                self._filters[hook_name] = [f for f in self._filters[hook_name] if f != filter_func]
                if not self._filters[hook_name]:
                    del self._filters[hook_name]
                    
    def remove_transformer(self, hook_name: str, transformer: Optional[DataTransformer] = None) -> None:
        if hook_name in self._transformers:
            if transformer is None:
                del self._transformers[hook_name]
            else:
                self._transformers[hook_name] = [t for t in self._transformers[hook_name] if t != transformer]
                if not self._transformers[hook_name]:
                    del self._transformers[hook_name]
                    
    def remove_validator(self, hook_name: str, validator: Optional[HookValidator] = None) -> None:
        if hook_name in self._validators:
            if validator is None:
                del self._validators[hook_name]
            else:
                self._validators[hook_name] = [v for v in self._validators[hook_name] if v != validator]
                if not self._validators[hook_name]:
                    del self._validators[hook_name]

class MiddlewareManager:
    def __init__(self):
        self._middleware_chains: Dict[str, MiddlewareChain] = {}
        self._global_middlewares: List[HookMiddleware] = []
        
    def add_middleware(self, hook_name: str, middleware: HookMiddleware, position: str = "pre") -> None:
        if hook_name not in self._middleware_chains:
            self._middleware_chains[hook_name] = MiddlewareChain([], [], [], [])
            
        chain = self._middleware_chains[hook_name]
        if position == "pre":
            chain.pre_middlewares.append(middleware)
        else:
            chain.post_middlewares.append(middleware)
            
    def add_global_middleware(self, middleware: HookMiddleware) -> None:
        self._global_middlewares.append(middleware)
        
    def process_before_execution(self, hook_name: str, args: tuple, kwargs: dict) -> tuple[tuple, dict]:
        processed_args, processed_kwargs = args, kwargs
        
        for middleware in self._global_middlewares:
            processed_args, processed_kwargs = middleware.before_execution(hook_name, processed_args, processed_kwargs)
            
        if hook_name in self._middleware_chains:
            for middleware in self._middleware_chains[hook_name].pre_middlewares:
                processed_args, processed_kwargs = middleware.before_execution(hook_name, processed_args, processed_kwargs)
                
        return processed_args, processed_kwargs
        
    def process_after_execution(self, hook_name: str, result: Any, execution) -> Any:
        processed_result = result
        
        if hook_name in self._middleware_chains:
            for middleware in reversed(self._middleware_chains[hook_name].post_middlewares):
                processed_result = middleware.after_execution(hook_name, processed_result, execution)
                
        for middleware in reversed(self._global_middlewares):
            processed_result = middleware.after_execution(hook_name, processed_result, execution)
            
        return processed_result
        
    def remove_middleware(self, hook_name: str, middleware: HookMiddleware) -> None:
        if hook_name in self._middleware_chains:
            chain = self._middleware_chains[hook_name]
            if middleware in chain.pre_middlewares:
                chain.pre_middlewares.remove(middleware)
            if middleware in chain.post_middlewares:
                chain.post_middlewares.remove(middleware)
                
    def remove_global_middleware(self, middleware: HookMiddleware) -> None:
        if middleware in self._global_middlewares:
            self._global_middlewares.remove(middleware)

class ConditionalFilter:
    def __init__(self, condition: Callable[..., bool]):
        self.condition = condition
        
    def should_execute(self, *args, **kwargs) -> bool:
        try:
            return self.condition(*args, **kwargs)
        except Exception:
            return False

class CompositeFilter:
    def __init__(self):
        self._filters: List[ConditionalFilter] = []
        self._operator: str = "and"
        
    def add_condition(self, condition: Callable[..., bool]) -> 'CompositeFilter':
        self._filters.append(ConditionalFilter(condition))
        return self
        
    def with_or_logic(self) -> 'CompositeFilter':
        self._operator = "or"
        return self
        
    def with_and_logic(self) -> 'CompositeFilter':
        self._operator = "and"
        return self
        
    def evaluate(self, *args, **kwargs) -> bool:
        if not self._filters:
            return True
            
        results = [f.should_execute(*args, **kwargs) for f in self._filters]
        
        if self._operator == "or":
            return any(results)
        else:
            return all(results)
