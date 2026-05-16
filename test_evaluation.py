#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""RAG评估指标系统使用示例"""

from utils.evaluation import (
    rag_evaluator,
    retrieval_evaluator,
    generation_evaluator
)

def test_retrieval_evaluation():
    """测试检索层评估"""
    print("=" * 60)
    print("测试检索层评估")
    print("=" * 60)

    query = "西班牙语发音规则"

    results = [
        {
            'id': 'doc_1',
            'content': '西班牙语共有27个字母，其中5个元音(a, e, i, o, u)和22个辅音。',
            'score': 0.85,
            'metadata': {'category': 'spanish'}
        },
        {
            'id': 'doc_2',
            'content': '西班牙语发音基础：元音a发音如"啊"，e发音如"诶"。',
            'score': 0.78,
            'metadata': {'category': 'spanish'}
        },
        {
            'id': 'doc_3',
            'content': '法语发音与西班牙语有所不同。',
            'score': 0.45,
            'metadata': {'category': 'french'}
        }
    ]

    relevant_docs = [
        '西班牙语共有27个字母，其中5个元音(a, e, i, o, u)和22个辅音。',
        '西班牙语发音基础：元音a发音如"啊"，e发音如"诶"。'
    ]

    metrics = retrieval_evaluator.evaluate(query, results, relevant_docs)

    print(f"\n查询: {query}")
    print(f"检索结果数: {len(results)}")
    print(f"\n检索评估指标:")
    print(f"  - 平均相似度: {metrics.avg_similarity:.4f}")
    print(f"  - 关键词匹配率: {metrics.keyword_match_rate:.4f}")
    print(f"  - Hit Rate: {metrics.hit_rate:.4f}")
    print(f"  - MRR: {metrics.mrr:.4f}")

    if metrics.recall_at_k:
        print(f"  - Recall@K:")
        for k, v in metrics.recall_at_k.items():
            print(f"      Recall@{k}: {v:.4f}")

    if metrics.ndcg_at_k:
        print(f"  - NDCG@K:")
        for k, v in metrics.ndcg_at_k.items():
            print(f"      NDCG@{k}: {v:.4f}")

    return metrics

def test_generation_evaluation():
    """测试生成层评估"""
    print("\n" + "=" * 60)
    print("测试生成层评估")
    print("=" * 60)

    query = "西班牙语元音发音"
    answer = "西班牙语有5个元音：a发音如'啊'，e发音如'诶'，i发音如'伊'，o发音如'喔'，u发音如'乌'。"
    retrieved_contexts = [
        "西班牙语共有27个字母，其中5个元音(a, e, i, o, u)和22个辅音。",
        "元音发音：a: 发音如'啊'，e: 发音如'诶'，i: 发音如'伊'，o: 发音如'喔'，u: 发音如'乌'。"
    ]

    metrics = generation_evaluator.evaluate(query, answer, retrieved_contexts)

    print(f"\n查询: {query}")
    print(f"答案: {answer}")
    print(f"\n生成评估指标:")
    print(f"  - 答案相关性: {metrics.answer_relevance:.4f}")
    print(f"  - 检索匹配率: {metrics.retrieval_match_rate:.4f}")
    print(f"  - 完整程度: {metrics.completeness:.4f}")
    print(f"  - 综合分数: {metrics.combined_score:.4f}")

    feedback = {
        'rating': 4,
        'feedback': '答案简洁准确',
        'thumbs_up': True,
        'timestamp': None
    }

    print(f"\n添加用户反馈: {feedback}")
    metrics_with_feedback = generation_evaluator.evaluate(
        query, answer, retrieved_contexts, feedback
    )

    print(f"\n反馈后综合分数: {metrics_with_feedback.combined_score:.4f}")

    stats = generation_evaluator.get_feedback_statistics()
    print(f"\n反馈统计:")
    print(f"  - 总反馈数: {stats['total_feedbacks']}")
    print(f"  - 正面比例: {stats['positive_ratio']:.2%}")
    print(f"  - 平均评分: {stats['avg_rating']:.2f}")
    print(f"  - 当前权重: alpha={stats['current_alpha']:.2f}, beta={stats['current_beta']:.2f}")

    return metrics

def test_comprehensive_evaluation():
    """测试综合评估"""
    print("\n" + "=" * 60)
    print("测试综合评估")
    print("=" * 60)

    session_id = "session_001"
    query = "Agent智能体是什么"

    retrieval_results = [
        {
            'id': 'doc_1',
            'content': 'Agent（智能代理）是一种能够感知环境、做出决策并执行动作的人工智能系统。',
            'score': 0.88,
            'metadata': {'category': 'agent'}
        },
        {
            'id': 'doc_2',
            'content': 'Agent具有自主性、反应性和主动性，能够自主完成复杂任务。',
            'score': 0.75,
            'metadata': {'category': 'agent'}
        }
    ]

    answer = "Agent是人工智能系统的一种，能够感知环境、做出决策并执行动作。它具有自主性、反应性和主动性。"

    retrieved_contexts = [
        r['content'] for r in retrieval_results
    ]

    relevant_docs = [r['content'] for r in retrieval_results]

    feedback = {
        'rating': 5,
        'thumbs_up': True
    }

    metrics = rag_evaluator.evaluate_interaction(
        session_id=session_id,
        query=query,
        retrieval_results=retrieval_results,
        answer=answer,
        retrieved_contexts=retrieved_contexts,
        relevant_docs=relevant_docs,
        feedback=feedback
    )

    print(f"\n会话ID: {session_id}")
    print(f"查询: {query}")
    print(f"综合评分: {metrics.overall_score:.4f}")

    if metrics.retrieval_metrics:
        print(f"\n检索评估:")
        print(f"  - 平均相似度: {metrics.retrieval_metrics.avg_similarity:.4f}")
        print(f"  - 关键词匹配率: {metrics.retrieval_metrics.keyword_match_rate:.4f}")
        print(f"  - Hit Rate: {metrics.retrieval_metrics.hit_rate:.4f}")

    if metrics.generation_metrics:
        print(f"\n生成评估:")
        print(f"  - 答案相关性: {metrics.generation_metrics.answer_relevance:.4f}")
        print(f"  - 检索匹配率: {metrics.generation_metrics.retrieval_match_rate:.4f}")
        print(f"  - 完整程度: {metrics.generation_metrics.completeness:.4f}")
        print(f"  - 用户评分: {metrics.generation_metrics.user_rating}")

    if metrics.improvement_suggestions:
        print(f"\n改进建议:")
        for i, suggestion in enumerate(metrics.improvement_suggestions, 1):
            print(f"  {i}. {suggestion}")

    summary = rag_evaluator.get_session_summary(session_id)
    print(f"\n会话摘要:")
    print(f"  - 交互次数: {summary['total_interactions']}")
    print(f"  - 平均综合分数: {summary['avg_overall_score']:.4f}")
    print(f"  - 平均检索分数: {summary['avg_retrieval_score']:.4f}")
    print(f"  - 平均生成分数: {summary['avg_generation_score']:.4f}")

    return metrics

def main():
    """主函数"""
    print("RAG评估指标系统演示")
    print("=" * 60)

    test_retrieval_evaluation()

    test_generation_evaluation()

    test_comprehensive_evaluation()

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
