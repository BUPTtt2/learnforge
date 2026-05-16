import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from config_loader import config

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    print("[Warning] Tavily module not found, using mock search")

class TavilySearch:
    """Tavily AI 搜索客户端"""

    def __init__(self):
        if not TAVILY_AVAILABLE:
            self.client = None
        else:
            self.api_key = config.TAVILY_API_KEY
            if not self.api_key:
                print("[Warning] Tavily API Key 未配置")
                self.client = None
            else:
                try:
                    self.client = TavilyClient(api_key=self.api_key)
                    print("[Success] Tavily client initialized")
                except Exception as e:
                    print(f"[Error] Tavily client initialization failed: {e}")
                    self.client = None

        self.search_history: List[Dict[str, Any]] = []
        self.max_history = 100

    def search(self, query: str, search_depth: str = "basic", **kwargs) -> dict:
        """执行搜索"""
        if not self.client:
            result = self._mock_response(query)
            self._add_to_history(query, result, search_depth)
            return result

        try:
            start_time = datetime.now()
            result = self.client.search(
                query=query,
                search_depth=search_depth,
                **kwargs
            )
            search_result = {
                "success": True,
                "results": result.get("results", []),
                "answer": result.get("answer", ""),
                "query": query,
                "search_depth": search_depth,
                "timestamp": start_time.isoformat(),
                "response_time": (datetime.now() - start_time).total_seconds()
            }
            self._add_to_history(query, search_result, search_depth)
            return search_result
        except Exception as e:
            print(f"[Error] Tavily search failed: {e}")
            result = self._mock_response(query)
            self._add_to_history(query, result, search_depth)
            return result

    def search_and_summarize(self, query: str, **kwargs) -> dict:
        """搜索并生成摘要"""
        if not self.client:
            result = self._mock_response(query)
            self._add_to_history(query, result, "basic")
            return result

        try:
            start_time = datetime.now()
            result = self.client.search(
                query=query,
                **kwargs
            )
            search_result = {
                "success": True,
                "summary": result.get("answer", ""),
                "results": result.get("results", []),
                "query": query,
                "search_depth": kwargs.get("search_depth", "basic"),
                "timestamp": start_time.isoformat(),
                "response_time": (datetime.now() - start_time).total_seconds()
            }
            self._add_to_history(query, search_result, kwargs.get("search_depth", "basic"))
            return search_result
        except Exception as e:
            print(f"[Error] Tavily search and summarize failed: {e}")
            result = self._mock_response(query)
            self._add_to_history(query, result, kwargs.get("search_depth", "basic"))
            return result

    def _add_to_history(self, query: str, result: dict, search_depth: str):
        """添加搜索到历史记录"""
        history_entry = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "success": result.get("success", False),
            "results_count": len(result.get("results", [])),
            "search_depth": search_depth,
            "response_time": result.get("response_time", 0)
        }
        self.search_history.append(history_entry)

        if len(self.search_history) > self.max_history:
            self.search_history = self.search_history[-self.max_history:]

    def get_search_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取搜索历史"""
        return self.search_history[-limit:]

    def get_search_stats(self) -> Dict[str, Any]:
        """获取搜索统计"""
        if not self.search_history:
            return {
                "total_searches": 0,
                "successful_searches": 0,
                "failed_searches": 0,
                "success_rate": 0.0,
                "avg_response_time": 0.0,
                "total_results": 0
            }

        successful = sum(1 for h in self.search_history if h["success"])
        total_response_time = sum(h["response_time"] for h in self.search_history)
        total_results = sum(h["results_count"] for h in self.search_history)

        return {
            "total_searches": len(self.search_history),
            "successful_searches": successful,
            "failed_searches": len(self.search_history) - successful,
            "success_rate": successful / len(self.search_history) * 100,
            "avg_response_time": total_response_time / len(self.search_history) if self.search_history else 0,
            "total_results": total_results
        }

    def clear_history(self):
        """清空搜索历史"""
        self.search_history = []

    def _mock_response(self, query: str) -> dict:
        """模拟响应（当API不可用时）"""
        return {
            "success": False,
            "results": [],
            "answer": f"关于'{query}'的搜索结果将在此显示",
            "query": query
        }

tavily_search = TavilySearch()
