print("="*50)
print("项目最短测试")
print("="*50)

# 1. 测试项目结构
print("\n[1/4] 检查项目结构...")
import os
dirs = ['agents', 'utils', 'sft_data', 'scripts', 'evaluation_logs']
for d in dirs:
    if os.path.exists(d):
        print(f"  ✅ {d}/")
    else:
        print(f"  ❌ {d}/")

# 2. 测试配置加载
print("\n[2/4] 测试配置加载...")
try:
    from config import MODEL_PATH, DEEPSEEK_MODEL
    print(f"  ✅ 配置加载成功")
    print(f"     模型路径: {MODEL_PATH}")
    print(f"     DeepSeek模型: {DEEPSEEK_MODEL}")
except Exception as e:
    print(f"  ❌ 配置加载失败: {e}")

# 3. 测试Agent模块
print("\n[3/4] 测试Agent模块...")
try:
    from agents.讲解师 import Explainer
    print(f"  ✅ 讲解师模块加载成功")
except Exception as e:
    print(f"  ❌ 讲解师模块加载失败: {e}")

# 4. 测试数据文件
print("\n[4/4] 检查数据文件...")
data_files = [
    'sft_data/merged_sft_data.json',
    'sft_data/filtered_data.json',
    'sft_output_final/adapter_model.safetensors'
]
for f in data_files:
    if os.path.exists(f):
        size = os.path.getsize(f) / 1024
        print(f"  ✅ {f} ({size:.1f} KB)")
    else:
        print(f"  ❌ {f}")

print("\n" + "="*50)
print("测试完成！")
print("="*50)