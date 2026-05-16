from collections import OrderedDict
from threading import Lock
from typing import Any, Optional


class LRUCache:
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            if self._is_expired(entry['timestamp']):
                del self.cache[key]
                return None
            
            self.cache.move_to_end(key)
            return entry['value']
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        with self.lock:
            ttl = ttl_seconds if ttl_seconds is not None else self.ttl_seconds
            
            if key in self.cache:
                self.cache.move_to_end(key)
            
            self.cache[key] = {
                'value': value,
                'timestamp': self._current_time(),
                'ttl': ttl
            }
            
            while len(self.cache) > self.max_size:
                self.cache.popitem(last=False)
    
    def has(self, key: str) -> bool:
        with self.lock:
            if key not in self.cache:
                return False
            
            entry = self.cache[key]
            if self._is_expired(entry['timestamp']):
                del self.cache[key]
                return False
            
            return True
    
    def delete(self, key: str):
        with self.lock:
            if key in self.cache:
                del self.cache[key]
    
    def clear(self):
        with self.lock:
            self.cache.clear()
    
    def size(self) -> int:
        with self.lock:
            return len(self.cache)
    
    def _is_expired(self, timestamp: float) -> bool:
        return (self._current_time() - timestamp) > self.cache.get(
            list(self.cache.keys())[0], {}
        ).get('ttl', self.ttl_seconds)
    
    def _current_time(self) -> float:
        import time
        return time.time()


lru_cache = LRUCache(max_size=200, ttl_seconds=7200)
