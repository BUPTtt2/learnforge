#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""集成ReAct + Memory + 改进缓存的完整测试"""

from agents.react_agent import react_agent
from agents.memory_system import memory_system
from utils.improved_cache import cache
from utils.rag import rag_system
from utils.evaluation import rag_evaluator, generation_evaluator


class IntegratedSystem:
    """集成系统"""
    
    def __init__(self):
        self.react = react_agent
        self.memory = memory_system
        self.cache = cache
        
        # 记录会话
        self.session_id = "test_session"
    
    def query(self, user_query: str, use_cache: bool = True) -> str:
        """完整查询流程"""
        print("=" * 60)
        print(f"Query: {user_query}")
        print("=" * 60)
        
        # 1. 检查缓存
        cache_key = f"query:{user_query}"
        if use_cache:
            cached = self.cache.get("query", user_query)
            if cached:
                print("[Cache Hit] 使用缓存结果")
                return cached
        
        # 2. 获取相关记忆
        memory_context = self.memory.get_context(user_query)
        print(f"[Memory] 检索到相关记忆")
        
        # 3. ReAct思考 + 工具调用
        print("\n[ReAct] 开始思考...")
        response = self.react.query(user_query, max_steps=2)
        
        # 4. 添加到短期记忆
        self.memory.add_short_term(f"用户问: {user_query}")
        self.memory.add_short_term(f"回答: {response}")
        
        # 5. 评估（可选）
        print("\n[Evaluation] 进行评估...")
        try:
            # 简单评估（获取RAG结果作为参考）
            rag_results = rag_system.search(user_query, top_k=3)
            
            # 评估检索质量
            retrieval_metrics = rag_evaluator.retrieval_evaluator.evaluate(user_query, rag_results)
            print(f"  检索平均相似度: {retrieval_metrics.avg_similarity:.4f}")
            print(f"  关键词匹配率: {retrieval_metrics.keyword_match_rate:.4f}")
        except Exception as e:
            print(f"  评估跳过: {e}")
        
        # 6. 缓存结果
        self.cache.set("query", user_query, response)
        
        # 7. 返回
        return response
    
    def get_system_status(self) -> str:
        """获取系统状态"""
        stats = []
        stats.append("=" * 60)
        stats.append("LearnForge 系统状态")
        stats.append("=" * 60)
        
        stats.append("\n【Memory System】")
        memory_stats = self.memory.summarize()
        stats.append(memory_stats)
        
        stats.append("\n【Cache System】")
        cache_stats = self.cache.get_stats()
        stats.append(f"L1 缓存: {cache_stats['l1_size']}项")
        stats.append(f"L2 缓存: {cache_stats['l2_size']}项")
        stats.append(f"命中率: {cache_stats['hit_rate']}")
        stats.append(f"详细: {cache_stats['hits']}")
        
        stats.append("\n【Knowledge Base】")
        kb_stats = rag_system.get_stats()
        stats.append(f"文档数: {kb_stats['document_count']}")
        stats.append(f"分块数: {kb_stats['chunk_count']}")
        
        stats.append("\n【Evaluation System】")
        feedback_stats = generation_evaluator.get_feedback_statistics()
        stats.append(f"总反馈: {feedback_stats['total_feedbacks']}")
        stats.append(f"正面比例: {feedback_stats['positive_ratio']:.1%}")
        stats.append(f"平均评分: {feedback_stats['avg_rating']:.1f}")
        stats.append(f"当前权重: α={feedback_stats['current_alpha']:.2f}, β={feedback_stats['current_beta']:.2f}")
        
        stats.append("\n" + "=" * 60)
        
        return "\n".join(stats)


def main():
    """主测试流程"""
    system = IntegratedSystem()
    
    # 1. 添加初始知识（模拟之前的学习）
    print("\n[1/5] 初始化系统...")
    memory_system.add_working("current_topic", "正在学习Agent系统和RAG")
    memory_system.add_short_term("用户对Agent系统感兴趣")
    
    # 2. 测试查询1
    print("\n[2/5] 测试查询1 - 西班牙语学习...")
    result = system.query("西班牙语发音有什么特点？")
    print(f"\n[Result]: {result}")
    
    # 3. 测试查询2 - 相关查询（利用记忆）
    print("\n[3/5] 测试查询2 - 相关问题...")
    result = system.query("西班牙语和中文发音有什么区别？")
    print(f"\n[Result]: {result[:200]}...")
    
    # 4. 测试查询3 - 需要工具调用
    print("\n[4/5] 测试查询3 - 触发工具调用...")
    result = system.query("什么是RAG系统？")
    print(f"\n[Result]: {result[:200]}...")
    
    # 5. 显示系统状态
    print("\n[5/5] 显示系统状态...")
    status = system.get_system_status()
    print(status)
    
    print("\n✅ 集成测试完成！")
    print("\n建议：")
    print("1. ReAct模式让模型可以自主决定工具调用")
    print("2. 分层记忆让对话有上下文")
    print("3. LRU缓存提升系统性能")
    print("4. 评估指标可以跟踪系统质量")


if __name__ == "__main__":
    main()
