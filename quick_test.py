#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""最短测试路径 - 快速验证RAG系统核心功能"""

import sys

def test_rag_search():
    """测试RAG搜索功能"""
    print("[1/4] 测试RAG搜索...")
    try:
        from utils.rag import rag_system
        results = rag_system.search("西班牙语学习", top_k=2)
        if results:
            print(f"  ✓ 搜索成功，找到 {len(results)} 条结果")
            for r in results:
                print(f"    - [分数: {r['score']:.2f}] {r['content'][:50]}...")
            return True
        else:
            print("  ✗ 搜索结果为空")
            return False
    except Exception as e:
        print(f"  ✗ 搜索失败: {e}")
        return False

def test_rag_stats():
    """测试RAG统计信息"""
    print("[2/4] 测试RAG统计...")
    try:
        from utils.rag import rag_system
        stats = rag_system.get_stats()
        print(f"  ✓ 文档数: {stats.get('document_count', 0)}")
        print(f"  ✓ 分块数: {stats.get('chunk_count', 0)}")
        return True
    except Exception as e:
        print(f"  ✗ 获取统计失败: {e}")
        return False

def test_evaluation():
    """测试评估指标系统"""
    print("[3/4] 测试评估指标...")
    try:
        from utils.evaluation import retrieval_evaluator, generation_evaluator
        
        # 测试检索评估
        results = [{'id': 'test', 'content': '西班牙语学习', 'score': 0.8}]
        metrics = retrieval_evaluator.evaluate("西班牙语", results)
        print(f"  ✓ 检索评估: 相似度={metrics.avg_similarity:.2f}")
        
        # 测试生成评估
        gen_metrics = generation_evaluator.evaluate(
            query="测试",
            answer="测试答案",
            retrieved_contexts=["测试上下文"]
        )
        print(f"  ✓ 生成评估: 相关性={gen_metrics.answer_relevance:.2f}")
        
        return True
    except Exception as e:
        print(f"  ✗ 评估测试失败: {e}")
        return False

def test_feedback():
    """测试用户反馈机制"""
    print("[4/4] 测试反馈机制...")
    try:
        from utils.evaluation import generation_evaluator
        
        feedback = {'rating': 5, 'thumbs_up': True}
        gen_metrics = generation_evaluator.evaluate(
            query="测试反馈",
            answer="测试答案",
            retrieved_contexts=["测试上下文"],
            feedback=feedback
        )
        
        stats = generation_evaluator.get_feedback_statistics()
        print(f"  ✓ 反馈统计: 总反馈={stats['total_feedbacks']}, 正面比例={stats['positive_ratio']:.1%}")
        return True
    except Exception as e:
        print(f"  ✗ 反馈测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("RAG系统最短测试路径")
    print("=" * 50)
    
    results = []
    
    results.append(("RAG搜索", test_rag_search()))
    results.append(("RAG统计", test_rag_stats()))
    results.append(("评估指标", test_evaluation()))
    results.append(("反馈机制", test_feedback()))
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("-" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"  {name}: {status}")
    
    print("\n" + "=" * 50)
    print(f"总结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查错误信息")
        return 1

if __name__ == "__main__":
    sys.exit(main())
