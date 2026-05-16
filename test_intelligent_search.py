#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试智能搜索决策机制"""

from utils.rag import rag_system

print('=== 测试1：搜索"大数据"（知识库中不存在）===')
result = rag_system.hybrid_search('大数据', use_external=True, quality_threshold=0.5)
print(f'检索质量: {result["retrieval_quality"]:.2f}')
print(f'触发外部搜索: {result["external_triggered"]}')
print(f'决策原因: {result["decision_reason"]}')
print()

print('=== 本地检索结果 ===')
for r in result['local']:
    print(f'  [相关度: {r["score"]:.2f}] {r["content"][:50]}...')

print()
print('=== 外部搜索结果 ===')
external = result.get('external', {})
if external and external.get('success'):
    print(f'  成功！摘要: {external.get("summary", "")[:150]}...')
else:
    print(f'  状态: {external.get("success", "未知")}')

print('\n' + '='*50)
print('=== 测试2：搜索"西班牙语学习"（知识库中存在）===')
result2 = rag_system.hybrid_search('西班牙语学习', use_external=True, quality_threshold=0.5)
print(f'检索质量: {result2["retrieval_quality"]:.2f}')
print(f'触发外部搜索: {result2["external_triggered"]}')
print(f'决策原因: {result2["decision_reason"]}')
print()

print('=== 本地检索结果 ===')
for r in result2['local']:
    print(f'  [相关度: {r["score"]:.2f}] {r["content"][:50]}...')
