import json

with open('sft_data/merged_sft_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"✅ 合并数据总数: {len(data)} 条")
avg_len = sum(len(d['output']) for d in data) / len(data)
print(f"📊 Output 平均长度: {avg_len:.0f} 字符")
print(f"📊 Output 总长度: {sum(len(d['output']) for d in data)} 字符")

# 显示前5条
print("\n📋 前5条数据:")
for i, d in enumerate(data[:5]):
    print(f"{i+1}. {d['instruction'][:50]}...")
