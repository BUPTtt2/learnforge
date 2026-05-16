import json

# 读取合并数据
with open('sft_data/merged_sft_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 转换为 alpaca 格式
alpaca_data = []
for item in data:
    alpaca_item = {
        "instruction": item["instruction"],
        "input": item.get("input", ""),
        "output": item["output"]
    }
    alpaca_data.append(alpaca_item)

# 保存为 JSONL 格式（LLaMA-Factory 支持）
output_path = 'sft_data/sft_data_for_llama.jsonl'
with open(output_path, 'w', encoding='utf-8') as f:
    for item in alpaca_data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print(f"✅ 转换完成: {len(alpaca_data)} 条数据")
print(f"📁 保存到: {output_path}")

# 同时保存为纯 JSON 格式（备用）
json_output = 'sft_data/sft_data_for_llama.json'
with open(json_output, 'w', encoding='utf-8') as f:
    json.dump(alpaca_data, f, ensure_ascii=False, indent=2)
print(f"📁 备份JSON: {json_output}")

# 显示前2条
print("\n📋 前2条数据示例:")
for i, item in enumerate(alpaca_data[:2]):
    print(f"\n{i+1}. {item['instruction'][:50]}...")
    print(f"   output: {item['output'][:100]}...")
