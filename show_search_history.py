#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""查看网络搜索记录和统计"""

from utils.tavily_client import tavily_search

print("=" * 60)
print("网络搜索记录查看")
print("=" * 60)

print("\n[1] 搜索统计")
print("-" * 60)
stats = tavily_search.get_search_stats()
print(f"  总搜索次数: {stats['total_searches']}")
print(f"  成功次数: {stats['successful_searches']}")
print(f"  失败次数: {stats['failed_searches']}")
print(f"  成功率: {stats['success_rate']:.1f}%")
print(f"  平均响应时间: {stats['avg_response_time']:.2f}秒")
print(f"  返回结果总数: {stats['total_results']}")

print("\n[2] 搜索历史 (最近10条)")
print("-" * 60)
history = tavily_search.get_search_history(limit=10)

if not history:
    print("  (暂无搜索记录)")
else:
    for i, h in enumerate(history, 1):
        status = "✅" if h['success'] else "❌"
        print(f"  {i}. [{status}] {h['query']}")
        print(f"     时间: {h['timestamp']}")
        print(f"     结果数: {h['results_count']}, 响应: {h['response_time']:.2f}秒")
        print()
