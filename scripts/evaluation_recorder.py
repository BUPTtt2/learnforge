"""SFT 数据评估记录系统"""

import json
import datetime
import os
from typing import Dict, List, Any

class EvaluationRecorder:
    def __init__(self, log_dir: str = "evaluation_logs"):
        self.log_dir = log_dir
        self.log_file = os.path.join(log_dir, "evaluation_history.json")
        self._ensure_log_dir()
        
    def _ensure_log_dir(self):
        """确保日志目录存在"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
    def _load_history(self) -> List[Dict]:
        """加载历史记录"""
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
        
    def _save_history(self, history: List[Dict]):
        """保存历史记录"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
            
    def record_evaluation(self, data_name: str, report: Dict, metadata: Dict = None):
        """记录一次评估结果"""
        timestamp = datetime.datetime.now().isoformat()
        
        record = {
            "timestamp": timestamp,
            "data_name": data_name,
            "report": report,
            "metadata": metadata or {}
        }
        
        history = self._load_history()
        history.append(record)
        self._save_history(history)
        
        print(f"\n✅ 评估已记录: {timestamp}")
        return record
        
    def get_latest_evaluation(self) -> Dict:
        """获取最新评估"""
        history = self._load_history()
        if history:
            return history[-1]
        return None
        
    def get_all_evaluations(self) -> List[Dict]:
        """获取所有评估"""
        return self._load_history()
        
    def compare_evaluations(self, idx1: int, idx2: int) -> Dict:
        """比较两次评估"""
        history = self._load_history()
        if idx1 >= len(history) or idx2 >= len(history):
            return {"error": "索引超出范围"}
            
        eval1 = history[idx1]
        eval2 = history[idx2]
        
        comparison = {
            "eval1": {"timestamp": eval1["timestamp"], "data": eval1["data_name"]},
            "eval2": {"timestamp": eval2["timestamp"], "data": eval2["data_name"]},
            "differences": {}
        }
        
        # 比较关键指标
        key_metrics = [
            ("数据概览", "总数据量"),
            ("内容质量", "平均质量分"),
            ("内容质量", "高分样本数 (>60)"),
            ("多样性分析", "主题覆盖数"),
        ]
        
        for section, metric in key_metrics:
            val1 = eval1["report"].get(section, {}).get(metric)
            val2 = eval2["report"].get(section, {}).get(metric)
            
            if val1 is not None and val2 is not None:
                diff = val2 - val1
                pct = (diff / val1 * 100) if val1 != 0 else 0
                comparison["differences"][f"{section}/{metric}"] = {
                    "before": val1,
                    "after": val2,
                    "diff": diff,
                    "change_pct": f"{pct:+.1f}%"
                }
                
        return comparison
        
    def print_summary(self):
        """打印评估历史摘要"""
        history = self._load_history()
        
        if not history:
            print("暂无评估记录")
            return
            
        print("\n" + "="*60)
        print(f"📊 评估历史 (共 {len(history)} 次)")
        print("="*60)
        
        for i, record in enumerate(history, 1):
            print(f"\n{i}. {record['timestamp']} - {record['data_name']}")
            
            # 关键指标
            overview = record['report'].get('数据概览', {})
            quality = record['report'].get('内容质量', {})
            diversity = record['report'].get('多样性分析', {})
            
            print(f"   数据量: {overview.get('总数据量', 'N/A')}")
            print(f"   质量分: {quality.get('平均质量分', 'N/A')}")
            print(f"   主题数: {diversity.get('主题覆盖数', 'N/A')}")
            
        # 打印最新的详细报告
        if history:
            print("\n" + "="*60)
            print("📋 最新评估详情:")
            print("="*60)
            latest = history[-1]
            
            for section, content in latest["report"].items():
                print(f"\n### {section}")
                if isinstance(content, dict):
                    for key, value in content.items():
                        print(f"  {key}: {value}")
