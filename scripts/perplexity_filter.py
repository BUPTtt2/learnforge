import json
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from typing import List, Dict, Any

class PerplexityFilter:
    def __init__(self, model_path: str = "D:\\Models\\Qwen3-4B", device: str = "auto"):
        self.model_path = model_path
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
        self.model.eval()
        print("Model loaded successfully!")
    
    def calculate_perplexity(self, text: str) -> float:
        if not text.strip():
            return float('inf')
        
        try:
            inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)
            with torch.no_grad():
                outputs = self.model(**inputs, labels=inputs["input_ids"])
                loss = outputs.loss
            
            ppl = torch.exp(loss).item()
            return ppl
        except Exception as e:
            print(f"Error calculating PPL: {e}")
            return float('inf')
    
    def filter_by_perplexity(self, data: List[Dict], threshold: float = 50.0) -> Dict[str, Any]:
        results = {
            "passed": [],
            "failed": [],
            "stats": {
                "total": len(data),
                "passed": 0,
                "failed": 0,
                "avg_ppl": 0.0,
                "min_ppl": float('inf'),
                "max_ppl": 0.0
            }
        }
        
        ppl_scores = []
        
        for item in data:
            text = item.get('output', '') + item.get('instruction', '')
            ppl = self.calculate_perplexity(text)
            ppl_scores.append(ppl)
            
            result_item = item.copy()
            result_item['ppl_score'] = ppl
            
            if ppl <= threshold:
                results["passed"].append(result_item)
            else:
                results["failed"].append(result_item)
        
        if ppl_scores:
            results["stats"]["avg_ppl"] = round(np.mean(ppl_scores), 2)
            results["stats"]["min_ppl"] = round(min(ppl_scores), 2)
            results["stats"]["max_ppl"] = round(max(ppl_scores), 2)
            results["stats"]["passed"] = len(results["passed"])
            results["stats"]["failed"] = len(results["failed"])
        
        return results
    
    def analyze_dataset(self, data_path: str) -> Dict[str, Any]:
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
        
        results = self.filter_by_perplexity(data)
        
        print("\n" + "="*60)
        print("📊 PPL 过滤分析报告")
        print("="*60)
        print(f"总样本数: {results['stats']['total']}")
        print(f"通过数: {results['stats']['passed']}")
        print(f"过滤数: {results['stats']['failed']}")
        print(f"平均 PPL: {results['stats']['avg_ppl']}")
        print(f"最小 PPL: {results['stats']['min_ppl']}")
        print(f"最大 PPL: {results['stats']['max_ppl']}")
        
        return results

if __name__ == "__main__":
    filter = PerplexityFilter()
    results = filter.analyze_dataset("sft_data/merged_sft_data.json")
    
    with open("sft_data/filtered_data.json", 'w', encoding='utf-8') as f:
        json.dump(results["passed"], f, ensure_ascii=False, indent=2)
    print("\n✅ 过滤后数据已保存到 sft_data/filtered_data.json")