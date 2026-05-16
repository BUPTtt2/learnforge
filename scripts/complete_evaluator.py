import json
import os
import sys
from typing import Dict, Any

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from evaluation_recorder import EvaluationRecorder

class CompleteEvaluator:
    def __init__(self):
        self.recorder = EvaluationRecorder("evaluation_logs")
    
    def run_full_evaluation(self, data_path: str, output_path: str = None) -> Dict[str, Any]:
        print("🔄 开始完整评估流程...")
        
        results = {
            "perplexity_filter": None,
            "llm_judge": None,
            "cross_consistency": None,
            "final_filtered_data": [],
            "summary": {}
        }
        
        print("\n1️⃣ 第一步: 困惑度过滤")
        try:
            from perplexity_filter import PerplexityFilter
            filter = PerplexityFilter()
            ppl_results = filter.analyze_dataset(data_path)
            results["perplexity_filter"] = ppl_results
            print("✅ 困惑度过滤完成")
        except Exception as e:
            print(f"⚠️  困惑度过滤失败: {e}")
        
        print("\n2️⃣ 第二步: LLM Judge 评分")
        try:
            from llm_judge import LLMJudge
            judge = LLMJudge(lora_path="sft_output_final")
            judge_results = judge.evaluate_dataset(data_path)
            results["llm_judge"] = judge_results
            print("✅ LLM Judge 评分完成")
        except Exception as e:
            print(f"⚠️  LLM Judge 评分失败: {e}")
        
        print("\n3️⃣ 第三步: 交叉一致性检验")
        try:
            from cross_consistency import CrossConsistencyChecker
            checker = CrossConsistencyChecker(lora_path="sft_output_final")
            consistency_results = checker.check_dataset_consistency(data_path, num_samples=5)
            results["cross_consistency"] = consistency_results
            print("✅ 交叉一致性检验完成")
        except Exception as e:
            print(f"⚠️  交叉一致性检验失败: {e}")
        
        print("\n4️⃣ 第四步: 综合过滤")
        results["final_filtered_data"] = self._combine_filters(results)
        print(f"✅ 综合过滤完成，保留 {len(results['final_filtered_data'])} 条高质量数据")
        
        print("\n5️⃣ 第五步: 生成报告")
        results["summary"] = self._generate_summary(results)
        self._print_summary(results["summary"])
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results["final_filtered_data"], f, ensure_ascii=False, indent=2)
            print(f"\n✅ 过滤后数据已保存到 {output_path}")
        
        try:
            self.recorder.record_evaluation(
                data_name=os.path.basename(data_path),
                report=results["summary"],
                metadata={
                    "data_path": data_path,
                    "num_samples": len(results["final_filtered_data"])
                }
            )
            print("✅ 评估结果已记录")
        except Exception as e:
            print(f"⚠️  记录评估结果失败: {e}")
        
        return results
    
    def _combine_filters(self, results: Dict[str, Any]) -> list:
        filtered = []
        
        if results["perplexity_filter"]:
            filtered.extend(results["perplexity_filter"]["passed"])
        
        if results["llm_judge"]:
            if not filtered:
                filtered = results["llm_judge"]["evaluations"]
            
            filtered = [
                item for item in filtered 
                if item.get("overall_score", 0) >= 6
            ]
        
        return filtered
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        summary = {}
        
        if results["perplexity_filter"]:
            ppl_stats = results["perplexity_filter"]["stats"]
            summary["perplexity_stats"] = {
                "total": ppl_stats["total"],
                "passed": ppl_stats["passed"],
                "avg_ppl": ppl_stats["avg_ppl"]
            }
        
        if results["llm_judge"]:
            judge_stats = results["llm_judge"]["stats"]
            summary["llm_judge_stats"] = {
                "avg_overall": judge_stats["avg_overall"],
                "high_quality": judge_stats["high_quality_count"],
                "medium_quality": judge_stats["medium_quality_count"],
                "low_quality": judge_stats["low_quality_count"]
            }
        
        if results["cross_consistency"]:
            consistency_stats = results["cross_consistency"]["summary"]
            summary["consistency_stats"] = {
                "avg_consistency": consistency_stats["avg_consistency"],
                "avg_similarity": consistency_stats["avg_similarity"]
            }
        
        summary["final_data_count"] = len(results["final_filtered_data"])
        summary["filter_rate"] = round(
            (1 - len(results["final_filtered_data"]) / 
             (results["perplexity_filter"]["stats"]["total"] if results["perplexity_filter"] else 1)) * 100, 2
        )
        
        return summary
    
    def _print_summary(self, summary: Dict[str, Any]):
        print("\n" + "="*60)
        print("📊 完整评估报告")
        print("="*60)
        
        if "perplexity_stats" in summary:
            print("\n1. 困惑度过滤:")
            print(f"   总样本: {summary['perplexity_stats']['total']}")
            print(f"   通过: {summary['perplexity_stats']['passed']}")
            print(f"   平均PPL: {summary['perplexity_stats']['avg_ppl']}")
        
        if "llm_judge_stats" in summary:
            print("\n2. LLM Judge评分:")
            print(f"   平均评分: {summary['llm_judge_stats']['avg_overall']}")
            print(f"   高质量: {summary['llm_judge_stats']['high_quality']}")
            print(f"   中等质量: {summary['llm_judge_stats']['medium_quality']}")
            print(f"   低质量: {summary['llm_judge_stats']['low_quality']}")
        
        if "consistency_stats" in summary:
            print("\n3. 交叉一致性:")
            print(f"   平均一致性: {summary['consistency_stats']['avg_consistency']}")
            print(f"   平均相似度: {summary['consistency_stats']['avg_similarity']}")
        
        print("\n4. 最终结果:")
        print(f"   过滤后数据量: {summary['final_data_count']}")
        print(f"   过滤率: {summary['filter_rate']}%")

if __name__ == "__main__":
    evaluator = CompleteEvaluator()
    results = evaluator.run_full_evaluation(
        data_path="sft_data/merged_sft_data.json",
        output_path="sft_data/filtered_data.json"
    )