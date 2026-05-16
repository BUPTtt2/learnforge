import psutil
import time
from threading import Lock
from typing import Optional


class MemoryMonitor:
    def __init__(self, max_memory_ratio: float = 0.8):
        self.max_memory_ratio = max_memory_ratio
        self.lock = Lock()
        self.is_memory_critical = False
        self.last_check_time = 0
        self.check_interval = 5
    
    def _get_memory_usage(self) -> float:
        try:
            memory = psutil.virtual_memory()
            return memory.percent / 100
        except Exception:
            return 0.5
    
    def _get_gpu_memory_usage(self) -> float:
        try:
            import torch
            if torch.cuda.is_available():
                total = torch.cuda.get_device_properties(0).total_memory
                used = torch.cuda.memory_allocated(0)
                return used / total
        except Exception:
            pass
        return 0.0
    
    def is_available(self) -> bool:
        return True
    
    def get_memory_status(self) -> dict:
        return {
            "cpu_memory": self._get_memory_usage(),
            "gpu_memory": self._get_gpu_memory_usage(),
            "is_available": True
        }


memory_monitor = MemoryMonitor(max_memory_ratio=0.99)