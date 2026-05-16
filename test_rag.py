#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""RAG系统最小闭环测试"""

from utils.rag import rag_system

print("=" * 60)
print("RAG系统最小闭环测试")
print("=" * 60)

# 1. 测试统计信息
print("\n[1/4] 测试统计信息...")
stats = rag_system.get_stats()
print("[OK] 知识库文档数量:", stats['document_count'])
print("[OK] 知识库分块数量:", stats['chunk_count'])

# 2. 测试搜索功能
print("\n[2/4] 测试搜索功能...")
test_queries = [
    "西班牙语学习",
    "Agent智能体",
    "LLM大语言模型",
    "RAG检索增强"
]

for query in test_queries:
    results = rag_system.search(query, top_k=2)
    print("\n搜索:", query)
    print("找到", len(results), "条结果")
    for i, r in enumerate(results, 1):
        print(f"  {i}. [分数: {r['score']:.2f}] {r['content'][:80]}...")

# 3. 测试添加文档
print("\n[3/4] 测试添加文档...")
test_content = """
这是一个测试文档，用于验证RAG系统的文档添加功能。
LearnForge是一个智能学习助手，支持西班牙语学习和AI相关知识。
"""
success = rag_system.add_document(test_content, {"source": "test", "category": "demo"})
print("[OK] 文档添加:", "成功" if success else "失败")

# 4. 测试新增文档搜索
print("\n[4/4] 测试新增文档搜索...")
results = rag_system.search("LearnForge智能学习助手", top_k=1)
print("找到", len(results), "条结果")
for r in results:
    print(f"  [分数: {r['score']:.2f}] {r['content'][:80]}...")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
