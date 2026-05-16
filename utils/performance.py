import time
import psutil
from typing import Dict, List, Optional
from datetime import datetime
from contextlib import contextmanager

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            "api_calls": 0,
            "api_errors": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_processing_time": 0.0,
            "memory_usage": [],
            "start_time": time.time()
        }
        self.operation_timings = []
    
    @contextmanager
    def measure(self, operation_name: str):
        start_time = time.time()
        try:
            yield
        finally:
            elapsed = time.time() - start_time
            self.record_timing(operation_name, elapsed)
    
    def record_timing(self, operation: str, duration: float):
        self.operation_timings.append({
            "operation": operation,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        })
        
        if len(self.operation_timings) > 1000:
            self.operation_timings = self.operation_timings[-1000:]
    
    def record_api_call(self, success: bool = True):
        self.metrics["api_calls"] += 1
        if not success:
            self.metrics["api_errors"] += 1
    
    def record_cache_access(self, hit: bool):
        if hit:
            self.metrics["cache_hits"] += 1
        else:
            self.metrics["cache_misses"] += 1
    
    def get_memory_usage(self) -> Dict:
        process = psutil.Process()
        memory_info = process.memory_info()
        
        memory_mb = memory_info.rss / 1024 / 1024
        
        self.metrics["memory_usage"].append({
            "timestamp": datetime.now().isoformat(),
            "memory_mb": memory_mb
        })
        
        if len(self.metrics["memory_usage"]) > 100:
            self.metrics["memory_usage"] = self.metrics["memory_usage"][-100:]
        
        return {
            "current_mb": memory_mb,
            "peak_mb": max([m["memory_mb"] for m in self.metrics["memory_usage"]], default=memory_mb),
            "average_mb": sum([m["memory_mb"] for m in self.metrics["memory_usage"]]) / len(self.metrics["memory_usage"]) if self.metrics["memory_usage"] else memory_mb
        }
    
    def get_uptime(self) -> float:
        return time.time() - self.metrics["start_time"]
    
    def get_summary(self) -> Dict:
        uptime = self.get_uptime()
        total_requests = self.metrics["api_calls"]
        error_rate = self.metrics["api_errors"] / total_requests if total_requests > 0 else 0
        
        cache_total = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        cache_hit_rate = self.metrics["cache_hits"] / cache_total if cache_total > 0 else 0
        
        recent_timings = self.operation_timings[-100:] if self.operation_timings else []
        avg_response_time = sum([t["duration"] for t in recent_timings]) / len(recent_timings) if recent_timings else 0
        
        memory_info = self.get_memory_usage()
        
        return {
            "uptime_seconds": uptime,
            "uptime_formatted": self._format_uptime(uptime),
            "total_api_calls": total_requests,
            "api_error_rate": f"{error_rate:.2%}",
            "cache_hit_rate": f"{cache_hit_rate:.1%}",
            "average_response_time": f"{avg_response_time:.3f}s",
            "memory_current_mb": f"{memory_info['current_mb']:.1f}",
            "memory_peak_mb": f"{memory_info['peak_mb']:.1f}",
            "operations_recorded": len(self.operation_timings)
        }
    
    def _format_uptime(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def get_operation_stats(self) -> List[Dict]:
        if not self.operation_timings:
            return []
        
        operation_groups = {}
        for timing in self.operation_timings:
            op = timing["operation"]
            if op not in operation_groups:
                operation_groups[op] = {
                    "operation": op,
                    "count": 0,
                    "total_time": 0.0,
                    "min_time": float('inf'),
                    "max_time": 0.0
                }
            
            operation_groups[op]["count"] += 1
            operation_groups[op]["total_time"] += timing["duration"]
            operation_groups[op]["min_time"] = min(operation_groups[op]["min_time"], timing["duration"])
            operation_groups[op]["max_time"] = max(operation_groups[op]["max_time"], timing["duration"])
        
        for op_data in operation_groups.values():
            op_data["avg_time"] = op_data["total_time"] / op_data["count"]
        
        return sorted(
            operation_groups.values(),
            key=lambda x: x["total_time"],
            reverse=True
        )
    
    def print_report(self):
        summary = self.get_summary()
        operation_stats = self.get_operation_stats()
        
        print("\n" + "="*60)
        print("📊 LearnForge 性能报告")
        print("="*60)
        
        print(f"\n⏱️  运行时间：{summary['uptime_formatted']}")
        print(f"🔧 总API调用：{summary['total_api_calls']}")
        print(f"❌ API错误率：{summary['api_error_rate']}")
        print(f"💾 缓存命中率：{summary['cache_hit_rate']}")
        print(f"⚡ 平均响应时间：{summary['average_response_time']}")
        print(f"🧠 当前内存：{summary['memory_current_mb']} MB (峰值: {summary['memory_peak_mb']} MB)")
        
        if operation_stats:
            print("\n📈 操作耗时统计：")
            print(f"{'操作':<30} {'次数':>6} {'平均':>10} {'总计':>10}")
            print("-"*60)
            for op_data in operation_stats[:5]:
                print(f"{op_data['operation']:<30} {op_data['count']:>6} {op_data['avg_time']:>9.3f}s {op_data['total_time']:>9.3f}s")
        
        print("\n" + "="*60)
    
    def reset(self):
        self.metrics = {
            "api_calls": 0,
            "api_errors": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_processing_time": 0.0,
            "memory_usage": [],
            "start_time": time.time()
        }
        self.operation_timings = []


performance_monitor = PerformanceMonitor()
