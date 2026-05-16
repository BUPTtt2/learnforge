import sys
sys.path.insert(0, '.')

from agents.commander import commander
from agents.讲解师 import explainer
from agents.审查师 import reviewer

print("=== 测试讲解师 ===")
try:
    result = explainer.generate_explanation('Python函数', mode='simple')
    print(f"讲解师结果: {result.get('validation')}")
    print(f"章节: {result.get('knowledge_point')}")
except Exception as e:
    print(f"讲解师失败: {e}")

print("\n=== 测试审查师预审查 ===")
try:
    chapters = ['Python函数']
    result = reviewer.pre_review_chapters('Python函数', chapters)
    print(f"预审查结果: {result}")
except Exception as e:
    print(f"预审查失败: {e}")

print("\n=== 测试章节处理 ===")
try:
    result = commander._process_single_chapter('Python函数', 'simple', '')
    print(f"章节处理结果: {result}")
except Exception as e:
    print(f"章节处理失败: {e}")

print("\n=== 测试Commander完整流程 ===")
try:
    result = commander.process_learning_request('Python函数', learning_mode='simple')
    print(f"Commander结果类型: {result.get('type')}")
    if 'error' in result:
        print(f"错误: {result.get('error')}")
    else:
        print(f"章节数: {len(result.get('chapters', []))}")
        print(f"结果数: {len(result.get('results', []))}")
except Exception as e:
    print(f"Commander失败: {e}")