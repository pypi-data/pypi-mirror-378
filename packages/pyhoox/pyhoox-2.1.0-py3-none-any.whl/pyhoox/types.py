from typing import Any, Callable, Dict, List, Optional, Union, TypeVar, Generic, Protocol, runtime_checkable
from typing import Awaitable, AsyncIterable, AsyncGenerator, Coroutine
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import asyncio

T = TypeVar('T', covariant=True)
P = TypeVar('P')
R = TypeVar('R')

HookCallback = Callable[..., Any]
AsyncHookCallback = Callable[..., Awaitable[Any]]
FilterFunction = Callable[[Any], Any]
ConditionFunction = Callable[..., bool]
ValidatorFunction = Callable[[Any], bool]

@dataclass(frozen=True)
class HookPriority:
    CRITICAL: int = 0
    HIGH: int = 25
    NORMAL: int = 50
    LOW: int = 75
    BACKGROUND: int = 100

class ExecutionStrategy(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel" 
    FAIL_FAST = "fail_fast"
    IGNORE_ERRORS = "ignore_errors"

class HookExecutionResult(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    FILTERED = "filtered"

@dataclass
class HookExecution:
    hook_name: str
    callback: HookCallback
    args: tuple
    kwargs: dict
    result: Any = None
    error: Optional[Exception] = None
    execution_time: float = 0.0
    status: HookExecutionResult = HookExecutionResult.SUCCESS

@dataclass
class HookMetadata:
    name: str
    callback: HookCallback
    priority: int = HookPriority.NORMAL
    once: bool = False
    condition: Optional[ConditionFunction] = None
    filter_func: Optional[FilterFunction] = None
    validator: Optional[ValidatorFunction] = None
    context: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: float = 0.0
    call_count: int = 0

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@runtime_checkable
class HookValidator(Protocol):
    def validate(self, data: Any) -> bool: ...
    def get_error_message(self) -> str: ...

@runtime_checkable 
class DataTransformer(Protocol):
    def transform(self, data: Any) -> Any: ...

@runtime_checkable
class HookMiddleware(Protocol):
    def before_execution(self, hook_name: str, args: tuple, kwargs: dict) -> tuple[tuple, dict]: ...
    def after_execution(self, hook_name: str, result: Any, execution: HookExecution) -> Any: ...

@runtime_checkable
class PersistenceBackend(Protocol):
    def save_hooks(self, hooks: Dict[str, List[HookMetadata]]) -> None: ...
    def load_hooks(self) -> Dict[str, List[HookMetadata]]: ...
    def delete_hooks(self, hook_name: str) -> None: ...

@runtime_checkable
class HookRegistry(Protocol[T]):
    def register(self, name: str, callback: Callable, **options) -> None: ...
    def unregister(self, name: str, callback: Optional[Callable] = None) -> None: ...
    def trigger(self, name: str, *args, **kwargs) -> T: ...
    def list_hooks(self, name: Optional[str] = None) -> Dict[str, List[HookMetadata]]: ...

@runtime_checkable
class AsyncHookRegistry(Protocol[T]):
    async def register(self, name: str, callback: AsyncHookCallback, **options) -> None: ...
    async def unregister(self, name: str, callback: Optional[AsyncHookCallback] = None) -> None: ...
    async def trigger(self, name: str, *args, **kwargs) -> T: ...
    async def list_hooks(self, name: Optional[str] = None) -> Dict[str, List[HookMetadata]]: ...

class HookError(Exception):
    pass

class HookValidationError(HookError):
    pass

class HookExecutionError(HookError):
    pass

class HookRegistrationError(HookError):
    pass

class HookNotFoundError(HookError):
    pass
