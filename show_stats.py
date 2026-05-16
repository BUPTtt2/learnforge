#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""查看当前评估统计"""

from utils.evaluation import generation_evaluator, rag_evaluator

print("=" * 50)
print("LearnForge 评估统计")
print("=" * 50)

print("\n[1] 反馈统计")
print("-" * 50)
stats = generation_evaluator.get_feedback_statistics()
print(f"  总反馈数: {stats['total_feedbacks']}")
print(f"  正面比例: {stats['positive_ratio']:.1%}")
print(f"  平均评分: {stats.get('avg_rating', 0):.1f}")
print(f"  当前权重: alpha={stats['current_alpha']:.2f}, beta={stats['current_beta']:.2f}")

print("\n[2] 会话摘要")
print("-" * 50)
summary = rag_evaluator.get_session_summary("session_001")
if summary:
    print(f"  会话ID: {summary.get('session_id', 'N/A')}")
    print(f"  交互次数: {summary.get('total_interactions', 0)}")
    print(f"  平均综合分数: {summary.get('avg_overall_score', 0):.2f}")
    print(f"  平均检索分数: {summary.get('avg_retrieval_score', 0):.2f}")
    print(f"  平均生成分数: {summary.get('avg_generation_score', 0):.2f}")
else:
    print("  暂无会话数据")

print("\n[3] 知识库状态")
print("-" * 50)
from utils.rag import rag_system
stats = rag_system.get_stats()
print(f"  文档数: {stats['document_count']}")
print(f"  分块数: {stats['chunk_count']}")

print("\n" + "=" * 50)
print("请在交互测试中给出反馈来积累评估数据！")
print("=" * 50)
