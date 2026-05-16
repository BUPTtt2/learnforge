import os
import json
import time
import hashlib
import random
import threading
from typing import Any, Optional, Dict
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

class CacheEntry:
    def __init__(self, key: str, value: Any, ttl: int = 3600):
        self.key = key
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.access_count = 0
        self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        return time.time() - self.created_at > self.ttl
    
    def access(self) -> Any:
        self.access_count += 1
        self.last_accessed = time.time()
        return self.value
    
    def to_dict(self) -> Dict:
        return {
            "key": self.key,
            "value": self.value,
            "created_at": self.created_at,
            "ttl": self.ttl,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CacheEntry':
        entry = cls(data["key"], data["value"], data["ttl"])
        entry.created_at = data["created_at"]
        entry.access_count = data["access_count"]
        entry.last_accessed = data["last_accessed"]
        return entry

class CacheManager:
    def __init__(self, persist_dir: str = "./cache_db", max_size: int = 1000, default_ttl: int = 3600):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(exist_ok=True)
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.memory_cache = {}
        self.stats = {
            "hits": 0,
            "misses": 0,
            "writes": 0,
            "evictions": 0,
            "penetration_skipped": 0,
            "breakdown_prevented": 0,
            "avalanche_prevented": 0
        }
        
        # 防穿透：空值缓存（存储不存在的key）
        self.null_cache = set()
        self.null_cache_ttl = 300  # 5分钟
        
        # 防击穿：互斥锁（防止缓存失效时大量请求同时查数据库）
        self.lock_dict = defaultdict(threading.Lock)
        
        # 防雪崩：随机ttl（缓存时间在基础ttl基础上随机波动）
        self.jitter_factor = 0.2  # 20%波动
        
        self._load_from_disk()
    
    def _generate_key(self, key: str) -> str:
        return hashlib.md5(str(key).encode('utf-8')).hexdigest()
    
    def _get_file_path(self, key: str) -> Path:
        hashed_key = self._generate_key(key)
        return self.persist_dir / f"{hashed_key}.json"
    
    def get(self, key: str, use_cache: bool = True) -> Optional[Any]:
        """
        缓存查询，集成了：
        1. 防穿透：检查空值缓存
        2. 防击穿：使用互斥锁
        """
        if not use_cache:
            return None
        
        # 防穿透：检查是否是已知的空值
        if key in self.null_cache:
            self.stats["penetration_skipped"] += 1
            print(f"[缓存穿透保护] 跳过已知空值: {key}")
            return None
        
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if not entry.is_expired():
                self.stats["hits"] += 1
                return entry.access()
            else:
                del self.memory_cache[key]
        
        file_path = self._get_file_path(key)
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    entry = CacheEntry.from_dict(data)
                    
                    if not entry.is_expired():
                        self.memory_cache[key] = entry
                        self.stats["hits"] += 1
                        return entry.access()
                    else:
                        try:
                            file_path.unlink()
                        except:
                            pass
            except Exception as e:
                print(f"[缓存读取错误] {e}")
        
        self.stats["misses"] += 1
        return None
    
    def get_with_lock(self, key: str, loader_func, use_cache: bool = True, ttl: Optional[int] = None) -> Any:
        """
        带互斥锁的缓存查询（防击穿）
        
        当缓存失效时，只有一个线程去查源数据，其他线程等待
        """
        cached = self.get(key, use_cache)
        if cached is not None:
            return cached
        
        # 获取互斥锁
        lock = self.lock_dict[key]
        with lock:
            # 双重检查：获取锁后再次确认缓存是否已被其他线程填充
            cached = self.get(key, use_cache)
            if cached is not None:
                self.stats["breakdown_prevented"] += 1
                print(f"[缓存击穿保护] 避免重复查询: {key}")
                return cached
            
            # 调用加载函数
            value = loader_func()
            
            # 防穿透：存储空值标记
            if value is None:
                self.add_null(key)
            else:
                self.set(key, value, ttl)
            
            return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存，集成了：
        1. 防雪崩：ttl加随机波动
        """
        if ttl is None:
            ttl = self.default_ttl
        
        # 防雪崩：ttl加入随机波动
        if ttl > 0:
            jitter = int(ttl * self.jitter_factor)
            ttl = ttl + random.randint(-jitter, jitter)
            ttl = max(60, ttl)  # 保证最小ttl为60秒
        
        if len(self.memory_cache) >= self.max_size:
            self._evict_lru()
        
        entry = CacheEntry(key, value, ttl)
        self.memory_cache[key] = entry
        self.stats["writes"] += 1
        
        # 移除空值标记（如果有的话）
        if key in self.null_cache:
            self.null_cache.remove(key)
        
        return self._persist_to_disk(key, entry)
    
    def add_null(self, key: str) -> bool:
        """
        防穿透：添加空值标记
        防止大量查询不存在的数据直接打到数据库
        """
        self.null_cache.add(key)
        self.stats["penetration_skipped"] += 1
        
        # 空值也要有过期时间，防止后续数据更新后无法获取
        self.set(f"__null_{key}", True, self.null_cache_ttl)
        
        print(f"[缓存穿透保护] 标记空值: {key}")
        return True
    
    def get_semantic_cache(self, knowledge_point: str, learning_mode: str, threshold: float = 0.8):
        """
        语义缓存：使用字符串相似度匹配
        支持模糊匹配，如"神经网络"和"什么是神经网络"可以命中同一缓存
        
        参数:
            knowledge_point: 知识点
            learning_mode: 学习模式
            threshold: 相似度阈值，默认0.8
        
        返回:
            缓存数据或None
        """
        import difflib
        
        for key, entry in self.memory_cache.items():
            # 只查找学习缓存
            if not key.startswith('learning:'):
                continue
            
            cached_data = entry.value
            cached_point = cached_data.get('knowledge_point', '')
            cached_mode = cached_data.get('mode', '')
            
            # 学习模式必须完全相同
            if cached_mode != learning_mode:
                continue
            
            # 计算字符串相似度
            similarity = difflib.SequenceMatcher(None, knowledge_point, cached_point).ratio()
            
            if similarity > threshold:
                print(f"[语义缓存] 命中: '{knowledge_point}' ≈ '{cached_point}' (相似度: {similarity:.2f})")
                self.stats["hits"] += 1  # 也算一次命中
                return cached_data
        
        # 内存没找到，查磁盘（简化处理：磁盘不做语义缓存）
        return None
    
    def remove_null(self, key: str) -> bool:
        """移除空值标记"""
        if key in self.null_cache:
            self.null_cache.remove(key)
        self.delete(f"__null_{key}")
        return True
    
    def _persist_to_disk(self, key: str, entry: CacheEntry) -> bool:
        file_path = self._get_file_path(key)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(entry.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[缓存写入错误] {e}")
            return False
    
    def _load_from_disk(self):
        for file_path in self.persist_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    entry = CacheEntry.from_dict(data)
                    if not entry.is_expired():
                        self.memory_cache[entry.key] = entry
            except Exception as e:
                print(f"[缓存加载错误] {e}")
    
    def _evict_lru(self):
        if not self.memory_cache:
            return
        
        lru_key = min(
            self.memory_cache.keys(),
            key=lambda k: self.memory_cache[k].last_accessed
        )
        
        file_path = self._get_file_path(lru_key)
        if file_path.exists():
            file_path.unlink()
        
        del self.memory_cache[lru_key]
        self.stats["evictions"] += 1
    
    def delete(self, key: str) -> bool:
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        file_path = self._get_file_path(key)
        if file_path.exists():
            file_path.unlink()
            return True
        
        return False
    
    def clear(self):
        self.memory_cache.clear()
        
        for file_path in self.persist_dir.glob("*.json"):
            try:
                file_path.unlink()
            except Exception as e:
                print(f"[缓存清理错误] {e}")
    
    def get_stats(self) -> Dict:
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0
        
        return {
            "memory_cache_size": len(self.memory_cache),
            "disk_cache_size": len(list(self.persist_dir.glob("*.json"))),
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": f"{hit_rate:.1%}",
            "writes": self.stats["writes"],
            "evictions": self.stats["evictions"],
            "penetration_skipped": self.stats["penetration_skipped"],
            "breakdown_prevented": self.stats["breakdown_prevented"],
            "avalanche_prevented": self.stats["avalanche_prevented"],
            "null_cache_size": len(self.null_cache)
        }
    
    def cleanup_expired(self):
        expired_keys = [
            key for key, entry in self.memory_cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            self.delete(key)
        
        return len(expired_keys)

cache_manager = CacheManager()
