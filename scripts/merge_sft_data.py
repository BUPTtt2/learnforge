import json
import os

# 合并所有扩充数据
data_files = [
    'sft_data/high_quality_sft_data_detailed.json',
    'sft_data/high_quality_sft_data_detailed_part2.json',
    'sft_data/high_quality_sft_data_detailed_part3.json',
    'sft_data/high_quality_sft_data_detailed_part4.json',
    'sft_data/high_quality_sft_data_detailed_part5.json'
]

all_data = []
for file_path in data_files:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_data.extend(data)
            print(f"✅ 加载 {file_path}: {len(data)} 条")

# 去重（基于 instruction）
seen_instructions = set()
unique_data = []
for item in all_data:
    if item['instruction'] not in seen_instructions:
        seen_instructions.add(item['instruction'])
        unique_data.append(item)

print(f"\n📊 合并后总数: {len(all_data)} 条")
print(f"📊 去重后总数: {len(unique_data)} 条")

# 保存合并数据
output_path = 'sft_data/merged_sft_data.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(unique_data, f, ensure_ascii=False, indent=2)

print(f"✅ 合并数据已保存到: {output_path}")

# 统计信息
total_length = sum(len(item['output']) for item in unique_data)
avg_length = total_length / len(unique_data) if unique_data else 0
print(f"\n📊 Output 平均长度: {avg_length:.0f} 字符")
