"""
SFT 数据质量评估与诊断系统
包含：训练前评估、训练中诊断、数据清洗
"""

import json
import re
import hashlib
from collections import Counter
from typing import Dict, List, Tuple
import numpy as np
import os
import sys

# 导入记录器
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
from evaluation_recorder import EvaluationRecorder

class SFTQualityEvaluator:
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

    def quality_report(self) -> Dict:
        """生成完整质量报告"""
        report = {
            "数据概览": self._basic_stats(),
            "格式一致性": self._format_check(),
            "内容质量": self._content_quality(),
            "多样性分析": self._diversity_analysis(),
            "毒性检测": self._toxicity_check(),
            "重复检测": self._duplication_check(),
            "异常值检测": self._outlier_detection(),
            "数据分布": self._distribution_audit()
        }
        return report

    def _basic_stats(self) -> Dict:
        """基础统计"""
        total = len(self.data)
        avg_instruction_len = np.mean([len(str(d.get('instruction', ''))) for d in self.data])
        avg_output_len = np.mean([len(str(d.get('output', ''))) for d in self.data])
        return {
            "总数据量": total,
            "平均 instruction 长度": round(avg_instruction_len, 1),
            "平均 output 长度": round(avg_output_len, 1),
            "空 input 比例": sum(1 for d in self.data if not d.get('input', '')) / total
        }

    def _format_check(self) -> Dict:
        """格式一致性检查"""
        issues = []
        required_fields = ['instruction', 'output']

        for i, item in enumerate(self.data):
            for field in required_fields:
                if field not in item or not item[field]:
                    issues.append(f"样本 {i}: 缺少或为空 {field}")

            if not isinstance(item.get('instruction', ''), str):
                issues.append(f"样本 {i}: instruction 不是字符串类型")
            if not isinstance(item.get('output', ''), str):
                issues.append(f"样本 {i}: output 不是字符串类型")

        return {
            "格式问题数": len(issues),
            "格式正确率": round((len(self.data) - len(issues) / len(required_fields)) / len(self.data) * 100, 1),
            "问题详情": issues[:10] if len(issues) > 10 else issues
        }

    def _content_quality(self) -> Dict:
        """内容质量评估"""
        quality_scores = []
        for item in self.data:
            output = str(item.get('output', ''))
            score = 0

            # 长度检查 (合理范围 100-2000 字符)
            if 100 <= len(output) <= 2000:
                score += 30

            # 包含专业术语标记
            tech_markers = ['#', '##', '**', '```', '1.', '2.', '-']
            if any(marker in output for marker in tech_markers):
                score += 20

            # 多段落检查
            if '\n\n' in output:
                score += 20

            # 包含代码块或列表
            if '```' in output or ('1.' in output and '2.' in output):
                score += 15

            # 避免简单回复
            if len(output) > 200 and not output.endswith(('。', '.', '!', '？')):
                score += 15

            quality_scores.append(score)

        return {
            "平均质量分": round(np.mean(quality_scores), 1),
            "质量分标准差": round(np.std(quality_scores), 1),
            "高分样本数 (>60)": sum(1 for s in quality_scores if s > 60),
            "低分样本数 (<30)": sum(1 for s in quality_scores if s < 30)
        }

    def _diversity_analysis(self) -> Dict:
        """多样性分析"""
        instructions = [str(d.get('instruction', '')) for d in self.data]
        first_words = [instr.split()[0] if instr else '' for instr in instructions]

        topics = []
        for item in self.data:
            instr = str(item.get('instruction', '')).lower()
            if any(k in instr for k in ['transformer', 'attention', 'bert', 'gpt']):
                topics.append('NLP/Transformer')
            elif any(k in instr for k in ['agent', 'react', 'langchain', 'tool']):
                topics.append('Agent')
            elif any(k in instr for k in ['rag', 'retrieval', 'vector']):
                topics.append('RAG')
            elif any(k in instr for k in ['lora', 'fine-tune', 'sft', '微调']):
                topics.append('Fine-tuning')
            elif any(k in instr for k in ['diffusion', 'stable', 'ddpm']):
                topics.append('Diffusion')
            else:
                topics.append('Other')

        topic_dist = Counter(topics)

        return {
            "主题分布": dict(topic_dist),
            "主题覆盖数": len(topic_dist),
            "最大占比主题": max(topic_dist.values()) / len(topics) * 100,
            "指令多样性": len(set(first_words)) / len(first_words) * 100
        }

    def _toxicity_check(self) -> Dict:
        """毒性/敏感词检测"""
        toxic_patterns = [
            r'傻逼', r'蠢货', r'废物', r'垃圾',
            r'fuck', r'shit', r'asshole', r'bitch'
        ]

        toxic_count = 0
        for item in self.data:
            content = str(item.get('instruction', '')) + str(item.get('output', ''))
            for pattern in toxic_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    toxic_count += 1
                    break

        return {
            "检测到毒性样本数": toxic_count,
            "毒性比例": round(toxic_count / len(self.data) * 100, 2),
            "安全性": "✅ 安全" if toxic_count == 0 else "⚠️ 存在毒性内容"
        }

    def _duplication_check(self) -> Dict:
        """重复检测"""
        hashes = []
        for item in self.data:
            content = str(item.get('instruction', '')) + '|' + str(item.get('output', ''))
            h = hashlib.md5(content.encode()).hexdigest()
            hashes.append(h)

        unique_hashes = len(set(hashes))
        dup_ratio = (1 - unique_hashes / len(hashes)) * 100

        # 句子级别重复检测
        repeat_sentences = 0
        for item in self.data:
            output = str(item.get('output', ''))
            lines = [l.strip() for l in output.split('\n') if l.strip()]
            if len(lines) > 3:
                for i, line in enumerate(lines):
                    if lines.count(line) > 1:
                        repeat_sentences += 1
                        break

        return {
            "唯一样本数": unique_hashes,
            "重复比例": round(dup_ratio, 2),
            "重复句子样本数": repeat_sentences,
            "去重建议": "需要去重" if dup_ratio > 5 else "无需去重"
        }

    def _outlier_detection(self) -> Dict:
        """异常值检测"""
        output_lens = [len(str(d.get('output', ''))) for d in self.data]

        q1, q3 = np.percentile(output_lens, [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outliers = [l for l in output_lens if l < lower_bound or l > upper_bound]

        return {
            "输出长度范围": f"{min(output_lens)} - {max(output_lens)}",
            "中位数": np.median(output_lens),
            "异常值数量": len(outliers),
            "异常值比例": round(len(outliers) / len(output_lens) * 100, 2),
            "异常值": outliers[:5] if outliers else "无"
        }

    def _distribution_audit(self) -> Dict:
        """数据分布审计"""
        output_lens = [len(str(d.get('output', ''))) for d in self.data]

        bins = [0, 200, 500, 800, 1200, 2000, float('inf')]
        labels = ['极短(<200)', '短(200-500)', '中(500-800)', '较长(800-1200)', '长(1200-2000)', '极长(>2000)']

        hist, _ = np.histogram(output_lens, bins=bins)
        dist = dict(zip(labels, hist.tolist()))

        return {
            "长度分布": dist,
            "建议": "分布不均" if max(hist) / min(hist[hist > 0]) > 10 else "分布合理"
        }


def print_report(report: Dict):
    """打印报告"""
    print("\n" + "="*60)
    print("📊 SFT 数据质量评估报告")
    print("="*60)

    for section, content in report.items():
        print(f"\n### {section}")
        if isinstance(content, dict):
            for key, value in content.items():
                status = "✅" if "建议" in key or "安全性" in key or "比例" not in key else ""
                print(f"  {key}: {value} {status}")
        else:
            print(f"  {content}")


if __name__ == "__main__":
    # 评估最终数据集
    data_path = r"D:\LLaMA-Factory\data\merged_sft_data_final.jsonl"
    data_name = "merged_sft_data_final"

    evaluator = SFTQualityEvaluator(data_path)
    report = evaluator.quality_report()
    print_report(report)
    
    # 记录评估结果
    try:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evaluation_logs")
        recorder = EvaluationRecorder(log_dir)
        recorder.record_evaluation(
            data_name=data_name,
            report=report,
            metadata={
                "data_path": data_path,
                "num_samples": report.get("数据概览", {}).get("总数据量", 0)
            }
        )
    except Exception as e:
        print(f"\n⚠️  记录评估结果失败: {e}")
