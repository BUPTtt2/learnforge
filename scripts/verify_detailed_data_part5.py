import json

# 读取第五部分扩充数据
with open('sft_data/high_quality_sft_data_detailed_part5.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"✅ 第五部分数据总量: {len(data)} 条\n")

# 统计 output 平均长度
total_length = sum(len(item['output']) for item in data)
avg_length = total_length / len(data)
print(f"📊 Output 平均长度: {avg_length:.0f} 字符\n")

# 打印每条数据的信息
print("📋 第五部分详细数据列表:\n")
for i, item in enumerate(data):
    output_preview = item['output'][:80].replace('\n', ' ')
    print(f"{i+1}. {item['instruction']}")
    print(f"   长度: {len(item['output'])} 字符")
    print(f"   预览: {output_preview}...")
    print()
