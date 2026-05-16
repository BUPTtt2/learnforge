#!/usr/bin/env python3
"""
提示词优化测试脚本
测试优化前后的提示词效果对比
"""

import sys
import os
import time
from agents.commander import commander

# 测试知识点
TEST_TOPICS = [
    "RAG (Retrieval-Augmented Generation)",
    "LangChain",
    "Agent 智能体"
]

# 测试学习目标
LEARNING_GOAL = "面试准备"

# 记录测试结果
results = []

def test_prompt(topic, learning_goal):
    """测试提示词效果"""
    print(f"\n=== 测试知识点: {topic} ===")
    print(f"学习目标: {learning_goal}")
    
    start_time = time.time()
    
    try:
        # 测试深度模式
        result = commander.process_learning_request(
            topic, 
            learning_mode="deep",
            learning_goal=learning_goal
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 分析结果
        chapters = len(result.get('chapters', []))
        total_content_length = 0
        exercise_count = 0
        
        for chapter_result in result.get('results', []):
            content = chapter_result.get('content', {})
            explanation = content.get('explanation', '')
            total_content_length += len(explanation)
            
            # 检查习题
            if 'exercises' in content:
                exercise_count += len(content['exercises'])
            elif 'exercise' in content:
                exercise_count += 1
        
        print(f"✓ 测试成功")
        print(f"- 章节数量: {chapters}")
        print(f"- 内容长度: {total_content_length} 字符")
        print(f"- 习题数量: {exercise_count}")
        print(f"- 执行时间: {execution_time:.2f} 秒")
        
        # 保存结果
        results.append({
            'topic': topic,
            'learning_goal': learning_goal,
            'chapters': chapters,
            'content_length': total_content_length,
            'exercise_count': exercise_count,
            'execution_time': execution_time,
            'success': True
        })
        
        return True
        
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"✗ 测试失败: {e}")
        print(f"- 执行时间: {execution_time:.2f} 秒")
        
        results.append({
            'topic': topic,
            'learning_goal': learning_goal,
            'error': str(e),
            'execution_time': execution_time,
            'success': False
        })
        
        return False

def generate_report():
    """生成测试报告"""
    print("\n" + "="*60)
    print("提示词优化测试报告")
    print("="*60)
    
    total_tests = len(results)
    success_tests = sum(1 for r in results if r['success'])
    
    print(f"测试总数: {total_tests}")
    print(f"成功测试: {success_tests}")
    print(f"成功率: {success_tests/total_tests*100:.1f}%")
    
    if success_tests > 0:
        avg_time = sum(r['execution_time'] for r in results if r['success']) / success_tests
        avg_content = sum(r['content_length'] for r in results if r['success']) / success_tests
        avg_chapters = sum(r['chapters'] for r in results if r['success']) / success_tests
        avg_exercises = sum(r['exercise_count'] for r in results if r['success']) / success_tests
        
        print(f"\n平均执行时间: {avg_time:.2f} 秒")
        print(f"平均内容长度: {avg_content:.0f} 字符")
        print(f"平均章节数量: {avg_chapters:.1f}")
        print(f"平均习题数量: {avg_exercises:.1f}")
    
    print("\n详细结果:")
    for i, result in enumerate(results, 1):
        status = "✓" if result['success'] else "✗"
        print(f"{i}. {status} {result['topic']}")
        if not result['success']:
            print(f"   错误: {result.get('error', '未知错误')}")
        else:
            print(f"   章节: {result['chapters']}, 内容: {result['content_length']} 字符, 习题: {result['exercise_count']}, 时间: {result['execution_time']:.2f}s")
    
    print("\n" + "="*60)

def main():
    """主函数"""
    print("开始测试优化后的提示词...")
    print(f"测试知识点: {', '.join(TEST_TOPICS)}")
    
    for topic in TEST_TOPICS:
        test_prompt(topic, LEARNING_GOAL)
    
    generate_report()

if __name__ == "__main__":
    main()
