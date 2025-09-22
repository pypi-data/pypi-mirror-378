from typing import Dict, List, Optional, Any
import weakref
from dataclasses import dataclass

from ..types import HookMetadata, HookExecution

@dataclass
class HookContext:
    name: str
    active: bool = True
    parent: Optional['HookContext'] = None
    children: List['HookContext'] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []

class ContextManager:
    def __init__(self):
        self._contexts: Dict[str, HookContext] = {}
        self._current_context: Optional[HookContext] = None
        self._context_stack: List[HookContext] = []
        
    def create_context(self, name: str, parent: Optional[str] = None) -> HookContext:
        parent_ctx = None
        if parent and parent in self._contexts:
            parent_ctx = self._contexts[parent]
            
        context = HookContext(name=name, parent=parent_ctx)
        self._contexts[name] = context
        
        if parent_ctx:
            parent_ctx.children.append(context)
            
        return context
        
    def get_context(self, name: str) -> Optional[HookContext]:
        return self._contexts.get(name)
        
    def activate_context(self, name: str) -> None:
        if name in self._contexts:
            self._current_context = self._contexts[name]
            self._current_context.active = True
            
    def deactivate_context(self, name: str) -> None:
        if name in self._contexts:
            self._contexts[name].active = False
            if self._current_context and self._current_context.name == name:
                self._current_context = None
                
    def push_context(self, name: str) -> None:
        if name in self._contexts:
            if self._current_context:
                self._context_stack.append(self._current_context)
            self._current_context = self._contexts[name]
            self._current_context.active = True
            
    def pop_context(self) -> Optional[HookContext]:
        if self._context_stack:
            previous_context = self._current_context
            self._current_context = self._context_stack.pop()
            if previous_context:
                previous_context.active = False
            return previous_context
        return None
        
    def get_current_context(self) -> Optional[HookContext]:
        return self._current_context
        
    def is_context_active(self, name: str) -> bool:
        context = self._contexts.get(name)
        return context.active if context else False
        
    def get_active_contexts(self) -> List[HookContext]:
        return [ctx for ctx in self._contexts.values() if ctx.active]
        
    def clear_context(self, name: str) -> None:
        if name in self._contexts:
            context = self._contexts[name]
            if context.parent:
                context.parent.children.remove(context)
            for child in context.children:
                child.parent = context.parent
            del self._contexts[name]

class HookNamespace:
    def __init__(self, name: str, context_manager: ContextManager):
        self.name = name
        self._context_manager = context_manager
        self._hooks: Dict[str, List[HookMetadata]] = {}
        
    def __enter__(self):
        self._context_manager.push_context(self.name)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._context_manager.pop_context()
        
    def register_hook(self, hook_name: str, hook_meta: HookMetadata) -> None:
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(hook_meta)
        
    def get_hooks(self, hook_name: str) -> List[HookMetadata]:
        return self._hooks.get(hook_name, [])
        
    def remove_hook(self, hook_name: str, callback: Optional[Any] = None) -> None:
        if hook_name in self._hooks:
            if callback is None:
                del self._hooks[hook_name]
            else:
                self._hooks[hook_name] = [h for h in self._hooks[hook_name] if h.callback != callback]
                if not self._hooks[hook_name]:
                    del self._hooks[hook_name]
