import json
import torch
import hashlib
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any

class CrossConsistencyChecker:
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
    
    def generate(self, instruction: str, temperature: float = 0.7, 
                 max_new_tokens: int = 300) -> str:
        prompt = f"Instruction: {instruction}\nOutput:"
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True
            )
        
        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return result.replace(prompt, "").strip()
    
    def calculate_similarity(self, texts: List[str]) -> float:
        if len(texts) < 2:
            return 1.0
        
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(texts)
        similarities = []
        
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                sim = cosine_similarity(tfidf_matrix[i], tfidf_matrix[j])[0][0]
                similarities.append(sim)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def calculate_content_diversity(self, texts: List[str]) -> float:
        if len(texts) < 2:
            return 0.0
        
        unique_hashes = set()
        for text in texts:
            text_hash = hashlib.md5(text.encode()).hexdigest()
            unique_hashes.add(text_hash)
        
        return len(unique_hashes) / len(texts)
    
    def check_consistency(self, instruction: str, num_generations: int = 5, 
                          temperature: float = 0.7) -> Dict[str, Any]:
        generations = []
        
        for i in range(num_generations):
            print(f"  Generating {i+1}/{num_generations}...")
            output = self.generate(instruction, temperature)
            generations.append(output)
        
        avg_length = sum(len(g) for g in generations) / len(generations)
        similarity = self.calculate_similarity(generations)
        diversity = self.calculate_content_diversity(generations)
        
        return {
            "instruction": instruction,
            "generations": generations,
            "stats": {
                "num_generations": num_generations,
                "avg_length": round(avg_length, 1),
                "avg_similarity": round(similarity, 4),
                "diversity": round(diversity, 4),
                "consistency_score": round((similarity * 0.6 + (1 - diversity) * 0.4) * 100, 2)
            }
        }
    
    def check_dataset_consistency(self, data_path: str, num_samples: int = 10, 
                                  num_generations: int = 3) -> Dict[str, Any]:
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
        
        samples_to_check = data[:min(num_samples, len(data))]
        
        results = {
            "results": [],
            "summary": {
                "total_samples": len(samples_to_check),
                "avg_consistency": 0.0,
                "avg_similarity": 0.0,
                "avg_diversity": 0.0,
                "high_consistency_count": 0,
                "medium_consistency_count": 0,
                "low_consistency_count": 0
            }
        }
        
        consistency_scores = []
        similarity_scores = []
        diversity_scores = []
        
        for i, item in enumerate(samples_to_check):
            instruction = item.get('instruction', '')
            print(f"\nChecking sample {i+1}/{len(samples_to_check)}...")
            print(f"Instruction: {instruction[:50]}...")
            
            result = self.check_consistency(instruction, num_generations)
            results["results"].append(result)
            
            consistency_scores.append(result["stats"]["consistency_score"])
            similarity_scores.append(result["stats"]["avg_similarity"])
            diversity_scores.append(result["stats"]["diversity"])
        
        if consistency_scores:
            results["summary"]["avg_consistency"] = round(sum(consistency_scores) / len(consistency_scores), 2)
            results["summary"]["avg_similarity"] = round(sum(similarity_scores) / len(similarity_scores), 4)
            results["summary"]["avg_diversity"] = round(sum(diversity_scores) / len(diversity_scores), 4)
            results["summary"]["high_consistency_count"] = sum(1 for s in consistency_scores if s >= 70)
            results["summary"]["medium_consistency_count"] = sum(1 for s in consistency_scores if 40 <= s < 70)
            results["summary"]["low_consistency_count"] = sum(1 for s in consistency_scores if s < 40)
        
        self._print_summary(results)
        return results
    
    def _print_summary(self, results: Dict[str, Any]):
        print("\n" + "="*60)
        print("📊 交叉一致性检验报告")
        print("="*60)
        print(f"检测样本数: {results['summary']['total_samples']}")
        print(f"\n统计指标:")
        print(f"  平均一致性分数: {results['summary']['avg_consistency']}")
        print(f"  平均相似度: {results['summary']['avg_similarity']}")
        print(f"  平均多样性: {results['summary']['avg_diversity']}")
        print(f"\n一致性分布:")
        print(f"  高一致性(≥70分): {results['summary']['high_consistency_count']}")
        print(f"  中等一致性(40-69分): {results['summary']['medium_consistency_count']}")
        print(f"  低一致性(<40分): {results['summary']['low_consistency_count']}")

if __name__ == "__main__":
    checker = CrossConsistencyChecker(lora_path="sft_output_final")
    results = checker.check_dataset_consistency("sft_data/merged_sft_data.json", 
                                                num_samples=10, 
                                                num_generations=3)
    
    with open("evaluation_logs/cross_consistency_results.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\n✅ 交叉一致性检验结果已保存到 evaluation_logs/cross_consistency_results.json")