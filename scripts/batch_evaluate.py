"""批量评估并记录所有数据集"""

import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from evaluation_recorder import EvaluationRecorder
from sft_quality_evaluator import SFTQualityEvaluator, print_report

def evaluate_and_record(data_path: str, data_name: str, log_dir: str):
    """评估并记录一个数据集"""
    print(f"\n{'='*60}")
    print(f"📊 评估数据集: {data_name}")
    print('='*60)
    
    try:
        evaluator = SFTQualityEvaluator(data_path)
        report = evaluator.quality_report()
        print_report(report)
        
        recorder = EvaluationRecorder(log_dir)
        recorder.record_evaluation(
            data_name=data_name,
            report=report,
            metadata={
                "data_path": data_path,
                "num_samples": report.get("数据概览", {}).get("总数据量", 0)
            }
        )
        return True
    except Exception as e:
        print(f"❌ 评估失败: {e}")
        return False

def main():
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evaluation_logs")
    
    datasets = [
        (r"D:\LLaMA-Factory\data\merged_sft_data.jsonl", "merged_sft_data (初始)"),
        (r"D:\LLaMA-Factory\data\merged_sft_data_augmented.jsonl", "merged_sft_data_augmented (补充Agent)"),
        (r"D:\LLaMA-Factory\data\merged_sft_data_cleaned.jsonl", "merged_sft_data_cleaned (清洗)"),
        (r"D:\LLaMA-Factory\data\merged_sft_data_final.jsonl", "merged_sft_data_final (最终)"),
    ]
    
    print("\n" + "="*60)
    print("🔍 开始批量评估所有数据集")
    print("="*60)
    
    for data_path, data_name in datasets:
        if os.path.exists(data_path):
            evaluate_and_record(data_path, data_name, log_dir)
        else:
            print(f"\n⚠️  数据集不存在: {data_path}")
    
    # 打印历史摘要
    print("\n" + "="*60)
    print("📋 评估历史摘要")
    print("="*60)
    recorder = EvaluationRecorder(log_dir)
    recorder.print_summary()
    
    # 比较第一次和最后一次评估
    history = recorder.get_all_evaluations()
    if len(history) >= 2:
        comparison = recorder.compare_evaluations(0, len(history)-1)
        print("\n" + "="*60)
        print("📈 初始 vs 最终 对比")
        print("="*60)
        for key, val in comparison["differences"].items():
            print(f"\n{key}:")
            print(f"  初始: {val['before']}")
            print(f"  最终: {val['after']}")
            print(f"  变化: {val['change_pct']}")

if __name__ == "__main__":
    main()
