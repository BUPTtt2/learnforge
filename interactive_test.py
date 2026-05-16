#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""交互式RAG搜索测试"""

from utils.rag import rag_system
import sys

def print_banner():
    print("=" * 70)
    print("""
    ██╗     ███████╗ █████╗ ██████╗ ███╗   ██╗███████╗ ██████╗ ███╗   ██╗
    ██║     ██╔════╝██╔══██╗██╔══██╗████╗  ██║██╔════╝██╔═══██╗████╗  ██║
    ██║     █████╗  ███████║██████╔╝██╔██╗ ██║█████╗  ██║   ██║██╔██╗ ██║
    ██║     ██╔══╝  ██╔══██║██╔══██╗██║╚██╗██║██╔══╝  ██║   ██║██║╚██╗██║
    ███████╗███████╗██║  ██║██║  ██║██║ ╚████║██║     ╚██████╔╝██║ ╚████║
    ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝      ╚═════╝ ╚═╝  ╚═══╝
    """)
    print("=" * 70)
    print("智能学习助手 - RAG 检索增强生成系统")
    print("=" * 70)
    print()

def main():
    print_banner()
    
    print("[系统状态]")
    stats = rag_system.get_stats()
    print(f"  - 知识库文档数: {stats['document_count']}")
    print(f"  - 分块数: {stats.get('chunk_count', 0)}")
    print()
    
    print("=== 快速测试 ===")
    quick_queries = [
        ("西班牙语发音基础", "spanish"),
        ("Agent智能体是什么", "agent"),
        ("LLM大语言模型", "llm"),
        ("RAG检索增强原理", "rag")
    ]
    
    for query, category in quick_queries:
        print(f"\n[查询] {query}")
        results = rag_system.search(query, top_k=2)
        if results:
            for i, r in enumerate(results, 1):
                score = r.get('score', 0)
                print(f"  [{i}] 分数: {score:.2f}")
                content = r.get('content', '')
                print(f"      {content[:120]}...")
        else:
            print("  [无结果]")
    
    print("\n" + "=" * 70)
    print("交互式查询模式 (输入 'q' 退出)")
    print("=" * 70)
    
    while True:
        try:
            query = input("\n请输入查询: ").strip()
            if query.lower() in ['q', 'quit', 'exit']:
                print("\n再见！")
                break
            
            if not query:
                continue
            
            print(f"\n搜索: \"{query}\"")
            print("-" * 70)
            
            results = rag_system.search(query, top_k=3)
            
            if results:
                for i, result in enumerate(results, 1):
                    score = result.get('score', 0)
                    content = result.get('content', '')
                    metadata = result.get('metadata', {})
                    
                    print(f"\n  [{i}] 相关度: {score:.2f}")
                    if metadata:
                        print(f"      元数据: {metadata}")
                    print(f"      内容: {content[:200]}...")
            else:
                print("  [未找到相关结果]")
                
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"\n[错误] {e}")

if __name__ == "__main__":
    main()
