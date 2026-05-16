"""
SFT 数据清洗策略
包含：格式清洗、去重、异常值处理、毒性过滤、数据分布平衡
"""

import json
import re
import hashlib
from collections import Counter
from typing import List, Dict, Set, Tuple
import numpy as np
import random


class SFTDataCleaner:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.data = []
        self.load_data()

    def load_data(self):
        """加载数据（支持 JSON 和 JSONL 格式）"""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        # 尝试 JSON 格式
        try:
            self.data = json.loads(content)
            print(f"✅ 数据加载完成（JSON）：{len(self.data)} 条")
            return
        except json.JSONDecodeError:
            pass

        # 尝试 JSONL 格式
        self.data = []
        for line in content.split('\n'):
            line = line.strip()
            if line:
                try:
                    self.data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        print(f"✅ 数据加载完成（JSONL）：{len(self.data)} 条")

    def clean_all(self) -> List[Dict]:
        """执行完整清洗流程"""
        print("\n开始数据清洗...")
        print("="*50)

        original_count = len(self.data)

        # 1. 格式清洗
        print("📋 1. 格式清洗...")
        self.data = self._format_clean()
        print(f"   格式清洗后: {len(self.data)} 条")

        # 2. 去重
        print("🔄 2. 去重...")
        before_dedup = len(self.data)
        self.data = self._deduplicate()
        print(f"   去重后: {len(self.data)} 条 (移除 {before_dedup - len(self.data)} 条)")

        # 3. 毒性过滤
        print("🛡️ 3. 毒性过滤...")
        before_toxic = len(self.data)
        self.data = self._remove_toxic()
        print(f"   毒性过滤后: {len(self.data)} 条 (移除 {before_toxic - len(self.data)} 条)")

        # 4. 异常值处理
        print("📊 4. 异常值处理...")
        before_outlier = len(self.data)
        self.data = self._remove_outliers()
        print(f"   异常值处理后: {len(self.data)} 条 (移除 {before_outlier - len(self.data)} 条)")

        # 5. 数据平衡
        print("⚖️ 5. 数据分布平衡...")
        self.data = self._balance_distribution()

        print("="*50)
        print(f"✅ 清洗完成: {original_count} → {len(self.data)} 条")
        print(f"   总共移除: {original_count - len(self.data)} 条 ({round((original_count - len(self.data)) / original_count * 100, 1)}%)")

        return self.data

    def _format_clean(self) -> List[Dict]:
        """格式清洗"""
        cleaned = []

        for item in self.data:
            # 确保必要字段存在
            if 'instruction' not in item or 'output' not in item:
                continue

            # 清洗文本
            instruction = str(item['instruction']).strip()
            output = str(item['output']).strip()
            input_text = str(item.get('input', '')).strip()

            # 移除空白字符
            instruction = re.sub(r'\s+', ' ', instruction)
            output = re.sub(r'\n{3,}', '\n\n', output)  # 超过2个换行压缩

            # 跳过空内容
            if len(instruction) < 5 or len(output) < 20:
                continue

            cleaned_item = {
                'instruction': instruction,
                'output': output,
                'input': input_text
            }
            cleaned.append(cleaned_item)

        return cleaned

    def _deduplicate(self) -> List[Dict]:
        """去重（MD5 + 模糊去重）"""
        seen_hashes: Set[str] = set()
        seen_content: Set[str] = set()
        deduplicated = []

        for item in self.data:
            # 精确去重（MD5）
            content_hash = hashlib.md5(
                (item.get('instruction', '') + '|' + item.get('output', '')).encode()
            ).hexdigest()

            if content_hash in seen_hashes:
                continue

            # 模糊去重（移除标点的文本）
            clean_content = re.sub(r'[^\w\u4e00-\u9fff]', '', item.get('output', ''))
            if clean_content[:50] in seen_content:
                continue

            seen_hashes.add(content_hash)
            seen_content.add(clean_content[:50])
            deduplicated.append(item)

        return deduplicated

    def _remove_toxic(self) -> List[Dict]:
        """毒性/敏感词过滤"""
        toxic_patterns = [
            r'傻[逼比]',
            r'蠢[货蛋]',
            r'废物',
            r'智障',
            r'白痴',
            r'垃圾(货|东西)?',
            r'fuck',
            r'shit',
            r'asshole',
            r'bitch',
            r'damn\s*it'
        ]

        clean_data = []

        for item in self.data:
            content = str(item.get('instruction', '')) + str(item.get('output', ''))

            is_toxic = False
            for pattern in toxic_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    is_toxic = True
                    break

            if not is_toxic:
                clean_data.append(item)

        return clean_data

    def _remove_outliers(self) -> List[Dict]:
        """异常值处理（长度异常）"""
        # 计算长度分布
        output_lens = [len(str(d.get('output', ''))) for d in self.data]

        if not output_lens:
            return self.data

        # IQR 方法检测异常值
        q1, q3 = np.percentile(output_lens, [15, 85])
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        # 确保合理范围
        lower = max(50, lower)  # 至少 50 字符
        upper = min(5000, upper)  # 最多 5000 字符

        cleaned = []
        for item in self.data:
            output_len = len(str(item.get('output', '')))
            if lower <= output_len <= upper:
                cleaned.append(item)

        return cleaned

    def _balance_distribution(self, max_per_topic: int = 30) -> List[Dict]:
        """数据分布平衡（限制每主题数量）"""
        # 主题分类
        topic_counts = Counter()
        balanced = []

        for item in self.data:
            instr = str(item.get('instruction', '')).lower()

            # 简单主题识别
            if any(k in instr for k in ['transformer', 'attention', 'bert', 'gpt', 'llm']):
                topic = 'NLP'
            elif any(k in instr for k in ['agent', 'react', 'langchain', 'tool calling']):
                topic = 'Agent'
            elif any(k in instr for k in ['rag', 'retrieval']):
                topic = 'RAG'
            elif any(k in instr for k in ['lora', 'fine-tune', 'sft', '微调', 'peft']):
                topic = 'Fine-tuning'
            elif any(k in instr for k in ['diffusion', 'stable', 'ddpm', '图像']):
                topic = 'Diffusion'
            elif any(k in instr for k in ['python', 'java', '代码', '编程']):
                topic = 'Programming'
            elif any(k in instr for k in ['学习', '方法', '技巧', '如何']):
                topic = 'General'
            else:
                topic = 'Other'

            if topic_counts[topic] < max_per_topic:
                topic_counts[topic] += 1
                balanced.append(item)

        return balanced

    def save_cleaned_data(self, output_path: str):
        """保存清洗后的数据"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print(f"✅ 清洗后数据已保存: {output_path}")


def main():
    input_path = r"D:\LLaMA-Factory\data\merged_sft_data.jsonl"
    output_path = r"D:\LLaMA-Factory\data\merged_sft_data_cleaned.jsonl"

    cleaner = SFTDataCleaner(input_path)
    cleaner.clean_all()
    cleaner.save_cleaned_data(output_path)


if __name__ == "__main__":
    main()
