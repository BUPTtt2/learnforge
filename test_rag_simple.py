#!/usr/bin/env python3
"""
简化的 RAG 系统测试脚本
跳过嵌入模型测试，专注于核心功能
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.rag import rag_system
from utils.tavily_client import tavily_search
from config_loader import config

def test_tavily_search():
    """测试 Tavily 搜索"""
    print("=== 测试 Tavily 搜索 ===")
    try:
        test_query = "Python RAG 系统实现"
        result = tavily_search.search(test_query, search_depth="basic")
        if result.get("success"):
            print(f"[Success] Tavily 搜索工作正常")
            print(f"结果数量: {len(result.get('results', []))}")
        else:
            print("[Warning] Tavily 搜索不可用，使用备用方案")
    except Exception as e:
        print(f"[Error] Tavily 搜索测试失败: {e}")

def test_rag_system_basic():
    """测试 RAG 系统基本功能"""
    print("\n=== 测试 RAG 系统基本功能 ===")
    try:
        # 测试统计信息
        stats = rag_system.get_collection_stats()
        print(f"[Info] 知识库统计: {stats}")
        
        # 测试混合搜索（不使用嵌入模型）
        test_query = "Python 语言"
        hybrid_results = rag_system.hybrid_search(test_query, use_external=True)
        if hybrid_results:
            print("[Success] 混合搜索工作正常")
            print(f"本地结果数量: {len(hybrid_results.get('local', []))}")
            print(f"外部搜索成功: {hybrid_results.get('external', {}).get('success', False)}")
        else:
            print("[Warning] 混合搜索失败")
            
    except Exception as e:
        print(f"[Error] RAG 系统测试失败: {e}")

def test_config():
    """测试配置"""
    print("\n=== 测试配置 ===")
    print(f"RAG 启用: {config.ENABLE_RAG}")
    print(f"Tavily 可用: {config.is_tavily_available()}")
    print(f"云端模型可用: {config.is_cloud_available()}")

def main():
    """主测试函数"""
    print("开始测试 RAG 系统...\n")
    
    test_config()
    test_tavily_search()
    test_rag_system_basic()
    
    print("\n测试完成！")

if __name__ == "__main__":
    main()