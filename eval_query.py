#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""实时查询评估"""

from utils.rag import rag_system
from utils.evaluation import rag_evaluator

query = "西班牙语学习"

print(f"=" * 50)
print(f"查询: {query}")
print(f"=" * 50)

result = rag_system.hybrid_search(query, use_external=True)
retrieval_results = result.get("local", [])
external_triggered = result.get("external_triggered", False)
retrieval_quality = result.get("retrieval_quality", 0)

print(f"\n[1] 检索结果")
print(f"-" * 50)
print(f"  本地结果数: {len(retrieval_results)}")
print(f"  触发外部搜索: {'是' if external_triggered else '否'}")
print(f"  检索质量: {retrieval_quality:.2f}")

if retrieval_results:
    print(f"\n  Top 3 结果:")
    for i, r in enumerate(retrieval_results[:3], 1):
        print(f"    {i}. [分数: {r['score']:.2f}] {r['content'][:50]}...")

print(f"\n[2] 检索评估指标")
print(f"-" * 50)

retrieval_metrics = rag_evaluator.retrieval_evaluator.evaluate(query, retrieval_results)
print(f"  平均相似度: {retrieval_metrics.avg_similarity:.4f}")
print(f"  关键词匹配率: {retrieval_metrics.keyword_match_rate:.4f}")
print(f"  Hit Rate: {retrieval_metrics.hit_rate:.4f}")
print(f"  MRR: {retrieval_metrics.mrr:.4f}")

if retrieval_metrics.ndcg_at_k:
    for k, v in retrieval_metrics.ndcg_at_k.items():
        print(f"  NDCG@{k}: {v:.4f}")

if retrieval_metrics.recall_at_k:
    for k, v in retrieval_metrics.recall_at_k.items():
        print(f"  Recall@{k}: {v:.4f}")

print(f"\n[3] 模拟答案评估")
print(f"-" * 50)
mock_answer = "西班牙语学习包括发音、词汇、语法等方面，需要多听多说多练。"
mock_contexts = [r['content'] for r in retrieval_results]

gen_metrics = rag_evaluator.generation_evaluator.evaluate(
    query=query,
    answer=mock_answer,
    retrieved_contexts=mock_contexts
)

print(f"  答案相关性: {gen_metrics.answer_relevance:.4f}")
print(f"  检索匹配率: {gen_metrics.retrieval_match_rate:.4f}")
print(f"  完整程度: {gen_metrics.completeness:.4f}")
print(f"  综合分数: {gen_metrics.completeness:.4f}")

print(f"\n[4] 添加反馈（可选）")
print(f"-" * 50)
feedback = {'rating': 5, 'thumbs_up': True, 'feedback': '评估测试'}
gen_metrics_with_feedback = rag_evaluator.generation_evaluator.evaluate(
    query=query,
    answer=mock_answer,
    retrieved_contexts=mock_contexts,
    feedback=feedback
)
print(f"  添加反馈后综合分数: {gen_metrics_with_feedback.combined_score:.4f}")

print(f"\n" + "=" * 50)
