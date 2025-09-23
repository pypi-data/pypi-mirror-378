from typing import Any, Dict, List, Optional, Union
import json
import pickle
import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path
import threading
import time

from ..types import HookMetadata, PersistenceBackend, HookError

class BasePersistenceBackend(ABC):
    @abstractmethod
    def save_hooks(self, hooks: Dict[str, List[HookMetadata]]) -> None:
        pass
        
    @abstractmethod
    def load_hooks(self) -> Dict[str, List[HookMetadata]]:
        pass
        
    @abstractmethod 
    def delete_hooks(self, hook_name: str) -> None:
        pass

class PicklePersistenceBackend(BasePersistenceBackend):
    def __init__(self, file_path: Union[str, Path] = "./pyhook_data/hooks.pkl"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        
    def save_hooks(self, hooks: Dict[str, List[HookMetadata]]) -> None:
        with self._lock:
            try:
                serializable_hooks = self._serialize_hooks(hooks)
                with open(self.file_path, 'wb') as f:
                    pickle.dump(serializable_hooks, f)
            except Exception as e:
                raise HookError(f"Failed to save hooks: {e}") from e
                
    def load_hooks(self) -> Dict[str, List[HookMetadata]]:
        with self._lock:
            if not self.file_path.exists():
                return {}
                
            try:
                with open(self.file_path, 'rb') as f:
                    serializable_hooks = pickle.load(f)
                return self._deserialize_hooks(serializable_hooks)
            except Exception as e:
                raise HookError(f"Failed to load hooks: {e}") from e
                
    def delete_hooks(self, hook_name: str) -> None:
        hooks = self.load_hooks()
        if hook_name in hooks:
            del hooks[hook_name]
            self.save_hooks(hooks)
            
    def _serialize_hooks(self, hooks: Dict[str, List[HookMetadata]]) -> Dict[str, List[Dict]]:
        serializable = {}
        for name, hook_list in hooks.items():
            serializable[name] = []
            for hook in hook_list:
                hook_dict = {
                    'name': hook.name,
                    'priority': hook.priority,
                    'once': hook.once,
                    'context': hook.context,
                    'tags': hook.tags,
                    'created_at': hook.created_at,
                    'call_count': hook.call_count
                }
                serializable[name].append(hook_dict)
        return serializable
        
    def _deserialize_hooks(self, serializable_hooks: Dict[str, List[Dict]]) -> Dict[str, List[HookMetadata]]:
        hooks = {}
        for name, hook_list in serializable_hooks.items():
            hooks[name] = []
            for hook_dict in hook_list:
                hook_meta = HookMetadata(
                    name=hook_dict['name'],
                    callback=lambda: None,  # Placeholder - callbacks can't be serialized
                    priority=hook_dict['priority'],
                    once=hook_dict['once'],
                    context=hook_dict['context'],
                    tags=hook_dict['tags'],
                    created_at=hook_dict['created_at']
                )
                hook_meta.call_count = hook_dict['call_count']
                hooks[name].append(hook_meta)
        return hooks

class JsonPersistenceBackend(BasePersistenceBackend):
    def __init__(self, file_path: Union[str, Path] = "./pyhook_data/hooks.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        
    def save_hooks(self, hooks: Dict[str, List[HookMetadata]]) -> None:
        with self._lock:
            try:
                serializable_hooks = self._serialize_hooks(hooks)
                with open(self.file_path, 'w') as f:
                    json.dump(serializable_hooks, f, indent=2)
            except Exception as e:
                raise HookError(f"Failed to save hooks: {e}") from e
                
    def load_hooks(self) -> Dict[str, List[HookMetadata]]:
        with self._lock:
            if not self.file_path.exists():
                return {}
                
            try:
                with open(self.file_path, 'r') as f:
                    serializable_hooks = json.load(f)
                return self._deserialize_hooks(serializable_hooks)
            except Exception as e:
                raise HookError(f"Failed to load hooks: {e}") from e
                
    def delete_hooks(self, hook_name: str) -> None:
        hooks = self.load_hooks()
        if hook_name in hooks:
            del hooks[hook_name]
            self.save_hooks(hooks)
            
    def _serialize_hooks(self, hooks: Dict[str, List[HookMetadata]]) -> Dict[str, List[Dict]]:
        serializable = {}
        for name, hook_list in hooks.items():
            serializable[name] = []
            for hook in hook_list:
                hook_dict = {
                    'name': hook.name,
                    'priority': hook.priority,
                    'once': hook.once,
                    'context': hook.context,
                    'tags': hook.tags,
                    'created_at': hook.created_at,
                    'call_count': hook.call_count
                }
                serializable[name].append(hook_dict)
        return serializable
        
    def _deserialize_hooks(self, serializable_hooks: Dict[str, List[Dict]]) -> Dict[str, List[HookMetadata]]:
        hooks = {}
        for name, hook_list in serializable_hooks.items():
            hooks[name] = []
            for hook_dict in hook_list:
                hook_meta = HookMetadata(
                    name=hook_dict['name'],
                    callback=lambda: None,
                    priority=hook_dict['priority'],
                    once=hook_dict['once'],
                    context=hook_dict['context'],
                    tags=hook_dict['tags'],
                    created_at=hook_dict['created_at']
                )
                hook_meta.call_count = hook_dict['call_count']
                hooks[name].append(hook_meta)
        return hooks

class SQLitePersistenceBackend(BasePersistenceBackend):
    def __init__(self, db_path: Union[str, Path] = "./pyhook_data/hooks.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()
        
    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS hooks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hook_name TEXT NOT NULL,
                    name TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    once BOOLEAN NOT NULL,
                    context TEXT,
                    tags TEXT,
                    created_at REAL NOT NULL,
                    call_count INTEGER DEFAULT 0
                )
            ''')
            conn.commit()
            
    def save_hooks(self, hooks: Dict[str, List[HookMetadata]]) -> None:
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute('DELETE FROM hooks')
                    
                    for hook_name, hook_list in hooks.items():
                        for hook in hook_list:
                            conn.execute('''
                                INSERT INTO hooks (hook_name, name, priority, once, context, tags, created_at, call_count)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                hook_name, hook.name, hook.priority, hook.once,
                                hook.context, json.dumps(hook.tags), hook.created_at, hook.call_count
                            ))
                    conn.commit()
            except Exception as e:
                raise HookError(f"Failed to save hooks: {e}") from e
                
    def load_hooks(self) -> Dict[str, List[HookMetadata]]:
        with self._lock:
            try:
                hooks = {}
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute('SELECT * FROM hooks ORDER BY hook_name, priority')
                    
                    for row in cursor:
                        hook_name = row[1]
                        tags = json.loads(row[6]) if row[6] else []
                        
                        hook_meta = HookMetadata(
                            name=row[2],
                            callback=lambda: None,
                            priority=row[3],
                            once=bool(row[4]),
                            context=row[5],
                            tags=tags,
                            created_at=row[7]
                        )
                        hook_meta.call_count = row[8]
                        
                        if hook_name not in hooks:
                            hooks[hook_name] = []
                        hooks[hook_name].append(hook_meta)
                        
                return hooks
            except Exception as e:
                raise HookError(f"Failed to load hooks: {e}") from e
                
    def delete_hooks(self, hook_name: str) -> None:
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute('DELETE FROM hooks WHERE hook_name = ?', (hook_name,))
                    conn.commit()
            except Exception as e:
                raise HookError(f"Failed to delete hooks: {e}") from e

class MemoryPersistenceBackend(BasePersistenceBackend):
    def __init__(self):
        self._storage: Dict[str, List[HookMetadata]] = {}
        self._lock = threading.Lock()
        
    def save_hooks(self, hooks: Dict[str, List[HookMetadata]]) -> None:
        with self._lock:
            self._storage = hooks.copy()
            
    def load_hooks(self) -> Dict[str, List[HookMetadata]]:
        with self._lock:
            return self._storage.copy()
            
    def delete_hooks(self, hook_name: str) -> None:
        with self._lock:
            if hook_name in self._storage:
                del self._storage[hook_name]

class PersistenceManager:
    def __init__(self, backend: Optional[BasePersistenceBackend] = None):
        self.backend = backend or PicklePersistenceBackend()
        self._auto_save = False
        self._save_interval = 60.0
        self._last_save = time.time()
        
    def set_auto_save(self, enabled: bool, interval: float = 60.0) -> None:
        self._auto_save = enabled
        self._save_interval = interval
        
    def should_auto_save(self) -> bool:
        if not self._auto_save:
            return False
        return (time.time() - self._last_save) >= self._save_interval
        
    def save_if_needed(self, hooks: Dict[str, List[HookMetadata]]) -> None:
        if self.should_auto_save():
            self.backend.save_hooks(hooks)
            self._last_save = time.time()
            
    def force_save(self, hooks: Dict[str, List[HookMetadata]]) -> None:
        self.backend.save_hooks(hooks)
        self._last_save = time.time()
        
    def load(self) -> Dict[str, List[HookMetadata]]:
        return self.backend.load_hooks()
        
    def delete(self, hook_name: str) -> None:
        self.backend.delete_hooks(hook_name)
