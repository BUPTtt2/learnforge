#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""改进的缓存系统 - LRU + 持久化"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import os


class LRUCache:
    """LRU缓存装饰器"""
    def __init__(self, maxsize: int = 1000, ttl: int = 86400):
        self.maxsize = maxsize
        self.ttl = ttl  # 默认24小时
        self.cache: Dict[str, Any] = {}
        self.access_order: Dict[str, int] = {}
        self.timestamps: Dict[str, float] = {}
        self.counter = 0
    
    def _clean_expired(self):
        """清理过期缓存"""
        now = time.time()
        expired_keys = [
            key for key, ts in self.timestamps.items()
            if now - ts > self.ttl
        ]
        for key in expired_keys:
            self._remove(key)
    
    def _remove(self, key: str):
        """移除缓存项"""
        if key in self.cache:
            del self.cache[key]
            del self.access_order[key]
            del self.timestamps[key]
    
    def _evict_lru(self):
        """淘汰最久未使用的"""
        if self.cache and len(self.cache) >= self.maxsize:
            lru_key = min(self.access_order, key=self.access_order.get)
            self._remove(lru_key)
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        self._clean_expired()
        if key in self.cache:
            # 更新访问顺序
            self.counter += 1
            self.access_order[key] = self.counter
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """设置缓存"""
        self._evict_lru()
        self.counter += 1
        self.cache[key] = value
        self.access_order[key] = self.counter
        self.timestamps[key] = time.time()
    
    def delete(self, key: str):
        """删除缓存"""
        self._remove(key)
    
    def clear(self):
        """清空所有缓存"""
        self.cache.clear()
        self.access_order.clear()
        self.timestamps.clear()


class PersistentLRUCache(LRUCache):
    """持久化LRU缓存"""
    def __init__(self, cache_path: str, maxsize: int = 1000, ttl: int = 86400):
        super().__init__(maxsize, ttl)
        self.cache_path = cache_path
        self._load()
    
    def _load(self):
        """从文件加载缓存"""
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cache = data.get('cache', {})
                    self.timestamps = data.get('timestamps', {})
                    self.access_order = data.get('access_order', {})
                    self.counter = data.get('counter', 0)
            except Exception as e:
                print(f"[Warning] Failed to load cache: {e}")
    
    def _save(self):
        """保存缓存到文件"""
        try:
            dir_path = os.path.dirname(self.cache_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path)
            
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'cache': self.cache,
                    'timestamps': self.timestamps,
                    'access_order': self.access_order,
                    'counter': self.counter
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Warning] Failed to save cache: {e}")
    
    def set(self, key: str, value: Any):
        """设置并保存"""
        super().set(key, value)
        self._save()
    
    def delete(self, key: str):
        """删除并保存"""
        super().delete(key)
        self._save()
    
    def clear(self):
        """清空并保存"""
        super().clear()
        self._save()


class MultiLayerCache:
    """多层缓存系统"""
    def __init__(self):
        # L1: 内存缓存（快速）
        self.memory_cache = LRUCache(maxsize=100, ttl=3600)  # 1小时
        
        # L2: 持久化缓存（慢速）
        cache_path = os.path.join(os.path.dirname(__file__), '../cache/cache.json')
        self.persist_cache = PersistentLRUCache(cache_path, maxsize=1000, ttl=86400)
        
        # 统计
        self.hits = {
            'memory': 0,
            'persist': 0,
            'miss': 0
        }
    
    def _get_key(self, prefix: str, content: str) -> str:
        """生成缓存key"""
        key_str = f"{prefix}:{content}"
        return hashlib.md5(key_str.encode('utf-8')).hexdigest()
    
    def get(self, prefix: str, content: str) -> Optional[Any]:
        """分层获取缓存"""
        key = self._get_key(prefix, content)
        
        # L1: 内存缓存
        value = self.memory_cache.get(key)
        if value is not None:
            self.hits['memory'] += 1
            return value
        
        # L2: 持久化缓存
        value = self.persist_cache.get(key)
        if value is not None:
            self.hits['persist'] += 1
            # 回填到L1
            self.memory_cache.set(key, value)
            return value
        
        self.hits['miss'] += 1
        return None
    
    def set(self, prefix: str, content: str, value: Any):
        """设置缓存"""
        key = self._get_key(prefix, content)
        self.memory_cache.set(key, value)
        self.persist_cache.set(key, value)
    
    def get_stats(self) -> Dict:
        """获取缓存统计"""
        total = sum(self.hits.values())
        hit_rate = (self.hits['memory'] + self.hits['persist']) / total if total > 0 else 0
        
        return {
            'hits': {
                'memory': self.hits['memory'],
                'persist': self.hits['persist'],
                'miss': self.hits['miss']
            },
            'hit_rate': f"{hit_rate:.1%}",
            'l1_size': len(self.memory_cache.cache),
            'l2_size': len(self.persist_cache.cache)
        }
    
    def clear_memory(self):
        """清空内存缓存"""
        self.memory_cache.clear()
    
    def clear_all(self):
        """清空所有缓存"""
        self.memory_cache.clear()
        self.persist_cache.clear()


# 全局实例
cache = MultiLayerCache()
