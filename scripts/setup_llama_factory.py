import json
import shutil
import os

# 复制数据到 LLaMA-Factory 的 data 目录
src = 'sft_data/sft_data_for_llama.jsonl'
dst = 'D:/LLaMA-Factory/data/merged_sft_data.jsonl'

# 读取数据
with open(src, 'r', encoding='utf-8') as f:
    data = [json.loads(line) for line in f]

print(f"✅ 数据读取完成: {len(data)} 条")

# 保存到 LLaMA-Factory
os.makedirs(os.path.dirname(dst), exist_ok=True)
with open(dst, 'w', encoding='utf-8') as f:
    for item in data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print(f"✅ 数据已复制到: {dst}")

# 更新 dataset_info.json
dataset_info_path = 'D:/LLaMA-Factory/data/dataset_info.json'
with open(dataset_info_path, 'r', encoding='utf-8') as f:
    dataset_info = json.load(f)

# 添加我们的数据集
dataset_info['merged_sft_data'] = {
    "file_name": "merged_sft_data.jsonl",
    "formatting": "alpaca",
    "columns": {
        "prompt": "instruction",
        "query": "input",
        "response": "output"
    },
    "tags": {
        "role_tag": "role",
        "content_tag": "content",
        "user_tag": "user",
        "assistant_tag": "assistant"
    }
}

with open(dataset_info_path, 'w', encoding='utf-8') as f:
    json.dump(dataset_info, f, ensure_ascii=False, indent=2)

print(f"✅ dataset_info.json 已更新")

# 创建训练命令
train_cmd = """cd D:\\LLaMA-Factory && llamafactory-cli train D:\\Appt\\大三下\\学习\\multi_Agent_智能日程\\learnforge\\llama_factory_config.yaml"""

print(f"\n📋 训练命令:")
print(train_cmd)
