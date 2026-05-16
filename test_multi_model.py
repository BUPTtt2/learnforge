# test_multi_model.py
from utils.multi_model import multi_model_manager

# 测试1：单模型生成
print("=" * 50)
print("测试1：简单任务（使用辅助模型 qwen3:4b）")
result = multi_model_manager.generate_content(
    "simple_explanation",
    "解释什么是RAG"
)
print(f"结果: {result[:200]}...")

print("\n" + "=" * 50)
print("测试2：复杂任务（使用主模型 qwen2.5:7b）")
result = multi_model_manager.generate_content(
    "deep_explanation",
    "详细讲解RAG的技术实现和项目实战"
)
print(f"结果: {result[:200]}...")

print("\n" + "=" * 50)
print("测试3：协作生成")
result = multi_model_manager.collaborative_generate(
    task="学习模式",
    context={
        "knowledge_point": "RAG",
        "learning_goal": "面试准备"
    }
)
print(f"快速摘要: {result['quick_summary'][:100]}...")
print(f"深度分析: {result['deep_analysis'][:100]}...")
print(f"相关概念: {result['related_concepts'][:100]}...")
print(f"习题: {result['exercises'][:100]}...")

print("\n" + "=" * 50)
print("所有测试完成！")
