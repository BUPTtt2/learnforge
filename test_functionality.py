#!/usr/bin/env python3
"""
LearnForge 功能测试脚本
验证系统核心功能的完整性
"""

import sys
import os
import time
from agents.commander import commander
from utils.storage import storage

# 测试结果记录
results = []

def test_core_functionality():
    """测试核心功能"""
    print("\n=== 测试核心功能 ===")
    
    # 测试1：知识点分析
    print("\n1. 测试知识点分析功能")
    try:
        result = commander.analyze_complexity("RAG")
        print(f"✓ 成功分析知识点: {result['knowledge_point']}")
        print(f"  复杂度: {result['complexity']}")
        print(f"  章节数量: {len(result['chapters'])}")
        results.append({"test": "知识点分析", "status": "成功", "details": f"章节数: {len(result['chapters'])}"})
    except Exception as e:
        print(f"✗ 失败: {e}")
        results.append({"test": "知识点分析", "status": "失败", "error": str(e)})
    
    # 测试2：学习内容生成
    print("\n2. 测试学习内容生成功能")
    try:
        result = commander.process_learning_request(
            "LangChain", 
            learning_mode="deep",
            learning_goal="面试准备"
        )
        chapters = len(result.get('chapters', []))
        exercises = 0
        for chapter_result in result.get('results', []):
            content = chapter_result.get('content', {})
            if 'exercises' in content:
                exercises += len(content['exercises'])
            elif 'exercise' in content:
                exercises += 1
        print(f"✓ 成功生成学习内容")
        print(f"  章节数量: {chapters}")
        print(f"  习题数量: {exercises}")
        results.append({"test": "学习内容生成", "status": "成功", "details": f"章节: {chapters}, 习题: {exercises}"})
    except Exception as e:
        print(f"✗ 失败: {e}")
        results.append({"test": "学习内容生成", "status": "失败", "error": str(e)})
    
    # 测试3：数据持久化
    print("\n3. 测试数据持久化功能")
    try:
        # 检查存储目录
        storage_dir = "learning_data"
        if os.path.exists(storage_dir):
            files = os.listdir(storage_dir)
            print(f"✓ 存储目录存在: {storage_dir}")
            print(f"  存储文件: {files}")
            # 测试加载历史
            history = storage.load_history()
            print(f"  历史记录数量: {len(history)}")
            results.append({"test": "数据持久化", "status": "成功", "details": f"文件: {len(files)}, 历史: {len(history)}"})
        else:
            print("✗ 存储目录不存在")
            results.append({"test": "数据持久化", "status": "失败", "error": "存储目录不存在"})
    except Exception as e:
        print(f"✗ 失败: {e}")
        results.append({"test": "数据持久化", "status": "失败", "error": str(e)})

def test_edge_cases():
    """测试边界情况"""
    print("\n=== 测试边界情况 ===")
    
    # 测试1：空输入
    print("\n1. 测试空输入处理")
    try:
        result = commander.analyze_complexity("")
        print(f"✓ 成功处理空输入")
        results.append({"test": "空输入处理", "status": "成功"})
    except Exception as e:
        print(f"✗ 失败: {e}")
        results.append({"test": "空输入处理", "status": "失败", "error": str(e)})
    
    # 测试2：特殊字符
    print("\n2. 测试特殊字符处理")
    try:
        result = commander.analyze_complexity("RAG&LangChain@Agent")
        print(f"✓ 成功处理特殊字符")
        results.append({"test": "特殊字符处理", "status": "成功"})
    except Exception as e:
        print(f"✗ 失败: {e}")
        results.append({"test": "特殊字符处理", "status": "失败", "error": str(e)})

def test_performance():
    """测试性能"""
    print("\n=== 测试性能 ===")
    
    # 测试响应时间
    print("\n1. 测试响应时间")
    start_time = time.time()
    try:
        result = commander.process_learning_request(
            "Python基础", 
            learning_mode="simple"
        )
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"✓ 响应时间: {execution_time:.2f} 秒")
        results.append({"test": "响应时间", "status": "成功", "details": f"{execution_time:.2f}秒"})
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"✗ 失败: {e}")
        results.append({"test": "响应时间", "status": "失败", "error": str(e)})

def generate_test_report():
    """生成测试报告"""
    print("\n" + "="*60)
    print("LearnForge 功能测试报告")
    print("="*60)
    
    total_tests = len(results)
    success_tests = sum(1 for r in results if r['status'] == "成功")
    
    print(f"测试总数: {total_tests}")
    print(f"成功测试: {success_tests}")
    print(f"成功率: {success_tests/total_tests*100:.1f}%")
    
    print("\n详细结果:")
    for i, result in enumerate(results, 1):
        status = "✓" if result['status'] == "成功" else "✗"
        print(f"{i}. {status} {result['test']}")
        if result['status'] == "失败":
            print(f"   错误: {result.get('error', '未知错误')}")
        elif 'details' in result:
            print(f"   详情: {result['details']}")
    
    print("\n" + "="*60)
    
    # 保存测试报告
    with open("test_report.txt", "w", encoding="utf-8") as f:
        f.write("LearnForge 功能测试报告\n")
        f.write("="*60 + "\n")
        f.write(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"测试总数: {total_tests}\n")
        f.write(f"成功测试: {success_tests}\n")
        f.write(f"成功率: {success_tests/total_tests*100:.1f}%\n")
        f.write("\n详细结果:\n")
        for i, result in enumerate(results, 1):
            status = "✓" if result['status'] == "成功" else "✗"
            f.write(f"{i}. {status} {result['test']}")
            if result['status'] == "失败":
                f.write(f" - 错误: {result.get('error', '未知错误')}\n")
            elif 'details' in result:
                f.write(f" - 详情: {result['details']}\n")
            else:
                f.write("\n")
    
    print("\n测试报告已保存到 test_report.txt")

def main():
    """主函数"""
    print("开始 LearnForge 功能测试...")
    
    # 测试核心功能
    test_core_functionality()
    
    # 测试边界情况
    test_edge_cases()
    
    # 测试性能
    test_performance()
    
    # 生成测试报告
    generate_test_report()

if __name__ == "__main__":
    main()
