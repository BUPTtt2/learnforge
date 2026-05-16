import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
from typing import List, Dict, Any

class LLMJudge:
    def __init__(self, model_path: str = "D:\\Models\\Qwen3-4B", 
                 lora_path: str = None, device: str = "auto"):
        self.model_path = model_path
        self.lora_path = lora_path
        self.device = device
        self.tokenizer = None
        self.model = None
        self._load_model()
    
    def _load_model(self):
        print("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        
        print("Loading model in 4-bit...")
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            quantization_config=bnb_config,
            device_map=self.device,
            trust_remote_code=True
        )
        
        if self.lora_path:
            print(f"Loading LoRA adapter from {self.lora_path}...")
            self.model = PeftModel.from_pretrained(self.model, self.lora_path)
        
        self.model.eval()
        print("Model loaded successfully!")
    
    def _build_prompt(self, instruction: str, output: str) -> str:
        prompt = f"""请作为专业评估者，对以下问答对进行质量评分。

【指令】: {instruction}

【回答】: {output}

请从以下维度评分（每项0-10分）：
1. 相关性：回答是否直接针对问题？
2. 准确性：信息是否正确无误？
3. 完整性：是否全面覆盖问题要点？
4. 深度：是否有足够的专业深度？
5. 清晰度：表达是否清晰易懂？

请输出JSON格式，包含各项分数和总体评价：
{{"relevance": 分数, "accuracy": 分数, "completeness": 分数, "depth": 分数, "clarity": 分数, "overall_score": 总分, "comment": "评价"}}
"""
        return prompt
    
    def score_sample(self, instruction: str, output: str) -> Dict[str, Any]:
        prompt = self._build_prompt(instruction, output)
        
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=200,
                    temperature=0.1,
                    do_sample=False
                )
            
            result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            result = result.replace(prompt, "").strip()
            
            try:
                score = json.loads(result)
                return score
            except json.JSONDecodeError:
                return self._parse_fallback(result)
        
        except Exception as e:
            print(f"Error scoring sample: {e}")
            return self._create_default_score()
    
    def _parse_fallback(self, text: str) -> Dict[str, Any]:
        import re
        scores = {}
        
        relevance_match = re.search(r'相关性[：:]?\s*(\d+)', text)
        accuracy_match = re.search(r'准确性[：:]?\s*(\d+)', text)
        completeness_match = re.search(r'完整性[：:]?\s*(\d+)', text)
        depth_match = re.search(r'深度[：:]?\s*(\d+)', text)
        clarity_match = re.search(r'清晰度[：:]?\s*(\d+)', text)
        
        scores["relevance"] = int(relevance_match.group(1)) if relevance_match else 5
        scores["accuracy"] = int(accuracy_match.group(1)) if accuracy_match else 5
        scores["completeness"] = int(completeness_match.group(1)) if completeness_match else 5
        scores["depth"] = int(depth_match.group(1)) if depth_match else 5
        scores["clarity"] = int(clarity_match.group(1)) if clarity_match else 5
        
        scores["overall_score"] = sum([scores[k] for k in ["relevance", "accuracy", "completeness", "depth", "clarity"]]) // 5
        scores["comment"] = "解析结果"
        
        return scores
    
    def _create_default_score(self) -> Dict[str, Any]:
        return {
            "relevance": 5,
            "accuracy": 5,
            "completeness": 5,
            "depth": 5,
            "clarity": 5,
            "overall_score": 5,
            "comment": "评分失败"
        }
    
    def evaluate_dataset(self, data_path: str) -> Dict[str, Any]:
        with open(data_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = []
            for line in content.split('\n'):
                line = line.strip()
                if line:
                    try:
                        data.append(json.loads(line))
                    except:
                        continue
        
        results = {
            "evaluations": [],
            "stats": {
                "total": len(data),
                "avg_relevance": 0.0,
                "avg_accuracy": 0.0,
                "avg_completeness": 0.0,
                "avg_depth": 0.0,
                "avg_clarity": 0.0,
                "avg_overall": 0.0,
                "high_quality_count": 0,
                "medium_quality_count": 0,
                "low_quality_count": 0
            }
        }
        
        relevance_scores = []
        accuracy_scores = []
        completeness_scores = []
        depth_scores = []
        clarity_scores = []
        overall_scores = []
        
        for i, item in enumerate(data):
            print(f"Evaluating sample {i+1}/{len(data)}...")
            
            instruction = item.get('instruction', '')
            output = item.get('output', '')
            
            score = self.score_sample(instruction, output)
            
            evaluation = item.copy()
            evaluation.update(score)
            results["evaluations"].append(evaluation)
            
            relevance_scores.append(score["relevance"])
            accuracy_scores.append(score["accuracy"])
            completeness_scores.append(score["completeness"])
            depth_scores.append(score["depth"])
            clarity_scores.append(score["clarity"])
            overall_scores.append(score["overall_score"])
        
        if overall_scores:
            results["stats"]["avg_relevance"] = round(sum(relevance_scores) / len(relevance_scores), 2)
            results["stats"]["avg_accuracy"] = round(sum(accuracy_scores) / len(accuracy_scores), 2)
            results["stats"]["avg_completeness"] = round(sum(completeness_scores) / len(completeness_scores), 2)
            results["stats"]["avg_depth"] = round(sum(depth_scores) / len(depth_scores), 2)
            results["stats"]["avg_clarity"] = round(sum(clarity_scores) / len(clarity_scores), 2)
            results["stats"]["avg_overall"] = round(sum(overall_scores) / len(overall_scores), 2)
            results["stats"]["high_quality_count"] = sum(1 for s in overall_scores if s >= 8)
            results["stats"]["medium_quality_count"] = sum(1 for s in overall_scores if 5 <= s < 8)
            results["stats"]["low_quality_count"] = sum(1 for s in overall_scores if s < 5)
        
        self._print_report(results)
        return results
    
    def _print_report(self, results: Dict[str, Any]):
        print("\n" + "="*60)
        print("📊 LLM Judge 评估报告")
        print("="*60)
        print(f"总样本数: {results['stats']['total']}")
        print(f"\n各项平均分:")
        print(f"  相关性: {results['stats']['avg_relevance']}")
        print(f"  准确性: {results['stats']['avg_accuracy']}")
        print(f"  完整性: {results['stats']['avg_completeness']}")
        print(f"  深度: {results['stats']['avg_depth']}")
        print(f"  清晰度: {results['stats']['avg_clarity']}")
        print(f"  综合评分: {results['stats']['avg_overall']}")
        print(f"\n质量分布:")
        print(f"  高质量(≥8分): {results['stats']['high_quality_count']}")
        print(f"  中等质量(5-7分): {results['stats']['medium_quality_count']}")
        print(f"  低质量(<5分): {results['stats']['low_quality_count']}")

if __name__ == "__main__":
    judge = LLMJudge(lora_path="sft_output_final")
    results = judge.evaluate_dataset("sft_data/merged_sft_data.json")
    
    with open("evaluation_logs/llm_judge_results.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\n✅ 评估结果已保存到 evaluation_logs/llm_judge_results.json")