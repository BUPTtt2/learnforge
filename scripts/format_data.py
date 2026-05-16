
import json

# 读取数据
input_file = "sft_data/high_quality_sft_data.json"
output_file = "sft_data/high_quality_sft_data_formatted.json"

data = json.load(open(input_file, "r", encoding="utf-8"))
print(f"✅ 数据总量: {len(data)} 条")

# 打印前几条示例
print("\n📋 前5条示例:")
for i, item in enumerate(data[:5]):
    print(f"\n{i+1}. {item['instruction']}")
    print(f"   {item['output'][:80]}...")

# 保存格式化后的版本
json.dump(data, open(output_file, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\n✅ 已保存格式化版本到: {output_file}")
