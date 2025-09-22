from typing import Any, Dict, List, Optional, Callable, Union
import logging
import time
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import threading

from ..types import HookExecution, HookExecutionResult, HookMetadata

@dataclass
class HookStats:
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    filtered_calls: int = 0
    cancelled_calls: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    min_execution_time: float = float('inf')
    max_execution_time: float = 0.0
    error_count: Dict[str, int] = field(default_factory=dict)
    
    def update(self, execution: HookExecution) -> None:
        self.total_calls += 1
        
        if execution.status == HookExecutionResult.SUCCESS:
            self.successful_calls += 1
        elif execution.status == HookExecutionResult.FAILED:
            self.failed_calls += 1
            if execution.error:
                error_type = type(execution.error).__name__
                self.error_count[error_type] = self.error_count.get(error_type, 0) + 1
        elif execution.status == HookExecutionResult.FILTERED:
            self.filtered_calls += 1
        elif execution.status == HookExecutionResult.CANCELLED:
            self.cancelled_calls += 1
            
        self.total_execution_time += execution.execution_time
        self.average_execution_time = self.total_execution_time / self.total_calls
        self.min_execution_time = min(self.min_execution_time, execution.execution_time)
        self.max_execution_time = max(self.max_execution_time, execution.execution_time)
        
    @property
    def success_rate(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return self.successful_calls / self.total_calls
        
    @property
    def failure_rate(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return self.failed_calls / self.total_calls

class HookLogger:
    def __init__(self, name: str = "pyhook", level: int = logging.ERROR):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
    def log_registration(self, hook_name: str, callback: Callable, **options) -> None:
        self.logger.info(
            f"Hook registered: {hook_name} -> {callback.__name__} "
            f"(priority: {options.get('priority', 'default')}, "
            f"once: {options.get('once', False)})"
        )
        
    def log_unregistration(self, hook_name: str, callback: Optional[Callable] = None) -> None:
        if callback:
            self.logger.info(f"Hook unregistered: {hook_name} -> {callback.__name__}")
        else:
            self.logger.info(f"All hooks unregistered for: {hook_name}")
            
    def log_trigger(self, hook_name: str, args: tuple, kwargs: dict) -> None:
        self.logger.debug(f"Triggering hook: {hook_name} with args: {args}, kwargs: {kwargs}")
        
    def log_execution(self, execution: HookExecution) -> None:
        if execution.status == HookExecutionResult.SUCCESS:
            self.logger.debug(
                f"Hook executed successfully: {execution.hook_name} -> "
                f"{execution.callback.__name__} ({execution.execution_time:.4f}s)"
            )
        elif execution.status == HookExecutionResult.FAILED:
            self.logger.error(
                f"Hook execution failed: {execution.hook_name} -> "
                f"{execution.callback.__name__}: {execution.error}"
            )
        elif execution.status == HookExecutionResult.FILTERED:
            self.logger.debug(
                f"Hook execution filtered: {execution.hook_name} -> "
                f"{execution.callback.__name__}"
            )
        elif execution.status == HookExecutionResult.CANCELLED:
            self.logger.warning(
                f"Hook execution cancelled: {execution.hook_name} -> "
                f"{execution.callback.__name__}"
            )
            
    def log_stats(self, hook_name: str, stats: HookStats) -> None:
        self.logger.info(
            f"Hook stats for {hook_name}: "
            f"calls: {stats.total_calls}, "
            f"success_rate: {stats.success_rate:.2%}, "
            f"avg_time: {stats.average_execution_time:.4f}s"
        )

class HookMonitor:
    def __init__(self, enable_logging: bool = True, enable_stats: bool = True):
        self._enable_logging = enable_logging
        self._enable_stats = enable_stats
        self._logger = HookLogger() if enable_logging else None
        self._stats: Dict[str, HookStats] = defaultdict(HookStats)
        self._lock = threading.Lock()
        self._execution_history: List[HookExecution] = []
        self._max_history = 1000
        
    def on_register(self, hook_name: str, callback: Callable, **options) -> None:
        if self._logger:
            self._logger.log_registration(hook_name, callback, **options)
            
    def on_unregister(self, hook_name: str, callback: Optional[Callable] = None) -> None:
        if self._logger:
            self._logger.log_unregistration(hook_name, callback)
            
    def on_trigger(self, hook_name: str, args: tuple, kwargs: dict) -> None:
        if self._logger:
            self._logger.log_trigger(hook_name, args, kwargs)
            
    def on_execution(self, execution: HookExecution) -> None:
        with self._lock:
            if self._enable_stats:
                self._stats[execution.hook_name].update(execution)
                
            if self._logger:
                self._logger.log_execution(execution)
                
            self._execution_history.append(execution)
            if len(self._execution_history) > self._max_history:
                self._execution_history = self._execution_history[-self._max_history:]
                
    def get_stats(self, hook_name: Optional[str] = None) -> Union[HookStats, Dict[str, HookStats]]:
        with self._lock:
            if hook_name:
                return self._stats.get(hook_name, HookStats())
            return dict(self._stats)
            
    def get_execution_history(self, 
                            hook_name: Optional[str] = None, 
                            limit: Optional[int] = None) -> List[HookExecution]:
        with self._lock:
            history = self._execution_history
            
            if hook_name:
                history = [e for e in history if e.hook_name == hook_name]
                
            if limit:
                history = history[-limit:]
                
            return history.copy()
            
    def reset_stats(self, hook_name: Optional[str] = None) -> None:
        with self._lock:
            if hook_name:
                if hook_name in self._stats:
                    del self._stats[hook_name]
            else:
                self._stats.clear()
                
    def clear_history(self) -> None:
        with self._lock:
            self._execution_history.clear()
            
    def get_top_performers(self, metric: str = "calls", limit: int = 10) -> List[tuple[str, Any]]:
        with self._lock:
            if metric == "calls":
                return sorted(
                    [(name, stats.total_calls) for name, stats in self._stats.items()],
                    key=lambda x: x[1], reverse=True
                )[:limit]
            elif metric == "success_rate":
                return sorted(
                    [(name, stats.success_rate) for name, stats in self._stats.items()],
                    key=lambda x: x[1], reverse=True
                )[:limit]
            elif metric == "avg_time":
                return sorted(
                    [(name, stats.average_execution_time) for name, stats in self._stats.items()],
                    key=lambda x: x[1]
                )[:limit]
            elif metric == "failure_rate":
                return sorted(
                    [(name, stats.failure_rate) for name, stats in self._stats.items()],
                    key=lambda x: x[1], reverse=True
                )[:limit]
            else:
                return []
                
    def get_slow_hooks(self, threshold: float = 1.0) -> List[tuple[str, float]]:
        with self._lock:
            return [
                (name, stats.average_execution_time) 
                for name, stats in self._stats.items() 
                if stats.average_execution_time > threshold
            ]
            
    def get_error_summary(self) -> Dict[str, Dict[str, int]]:
        with self._lock:
            summary = {}
            for hook_name, stats in self._stats.items():
                if stats.error_count:
                    summary[hook_name] = dict(stats.error_count)
            return summary
            
    def print_summary(self, hook_name: Optional[str] = None) -> None:
        if hook_name:
            stats = self.get_stats(hook_name)
            if isinstance(stats, HookStats):
                print(f"\n=== Hook Stats: {hook_name} ===")
                print(f"Total calls: {stats.total_calls}")
                print(f"Success rate: {stats.success_rate:.2%}")
                print(f"Failure rate: {stats.failure_rate:.2%}")
                print(f"Average execution time: {stats.average_execution_time:.4f}s")
                print(f"Min execution time: {stats.min_execution_time:.4f}s")
                print(f"Max execution time: {stats.max_execution_time:.4f}s")
                if stats.error_count:
                    print("Errors:")
                    for error_type, count in stats.error_count.items():
                        print(f"  {error_type}: {count}")
        else:
            all_stats = self.get_stats()
            if isinstance(all_stats, dict):
                print("\n=== Overall Hook Stats ===")
                total_calls = sum(s.total_calls for s in all_stats.values())
                total_successful = sum(s.successful_calls for s in all_stats.values())
                total_failed = sum(s.failed_calls for s in all_stats.values())
                
                print(f"Total hooks: {len(all_stats)}")
                print(f"Total calls: {total_calls}")
                print(f"Overall success rate: {total_successful/total_calls:.2%}" if total_calls > 0 else "No calls")
                print(f"Overall failure rate: {total_failed/total_calls:.2%}" if total_calls > 0 else "No failures")

class DebugHookRegistry:
    def __init__(self, registry, monitor: Optional[HookMonitor] = None):
        self._registry = registry
        self._monitor = monitor or HookMonitor()
        
    def register(self, name: str, callback: Callable, **options) -> None:
        self._monitor.on_register(name, callback, **options)
        return self._registry.register(name, callback, **options)
        
    def unregister(self, name: str, callback: Optional[Callable] = None) -> None:
        self._monitor.on_unregister(name, callback)
        return self._registry.unregister(name, callback)
        
    def trigger(self, name: str, *args, **kwargs) -> Any:
        self._monitor.on_trigger(name, args, kwargs)
        return self._registry.trigger(name, *args, **kwargs)
        
    def get_monitor(self) -> HookMonitor:
        return self._monitor
        
    def __getattr__(self, name: str) -> Any:
        return getattr(self._registry, name)
