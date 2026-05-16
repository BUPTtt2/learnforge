#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多Agent架构
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.commander import commander


def test_multi_agent():
    print("="*60)
    print("🚀 测试多Agent架构")
    print("="*60)
    
    # 测试知识点
    knowledge_point = "Transformer架构"
    learning_mode = "simple"
    learning_goal = "理解基础概念"
    
    print(f"\n📚 测试知识点: {knowledge_point}")
    print(f"🎯 学习模式: {learning_mode}")
    print("="*60)
    
    try:
        # 调用Commander处理
        result = commander.process_learning_request(
            knowledge_point,
            learning_mode,
            learning_goal
        )
        
        print(f"\n✅ 处理完成!")
        print(f"📊 类型: {result['type']}")
        print(f"📚 章节数: {len(result['chapters'])}")
        
        # 显示第一个章节
        if result['results']:
            first_chapter = result['results'][0]
            print(f"\n📖 第一个章节: {first_chapter['chapter']}")
            print("\n📝 讲解内容:")
            print("-"*40)
            explanation = first_chapter['content'].get('explanation', '')
            if len(explanation) > 300:
                print(explanation[:300] + "...")
            else:
                print(explanation)
            
            print("\n❓ 习题:")
            print("-"*40)
            exercise = first_chapter['exercise'].get('exercise', {})
            print(f"题目: {exercise.get('question', '')}")
            for opt in exercise.get('options', []):
                print(f"  {opt}")
            print(f"答案: {exercise.get('answer', '')}")
        
        print("\n" + "="*60)
        print("🎉 多Agent架构测试成功!")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_multi_agent()
