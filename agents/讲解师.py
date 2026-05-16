from typing import Dict, Any, Optional, Tuple
import json
import re
from utils.web_utils import web_search_tool
from utils.model_utils import hybrid_model_manager
from config_loader import config
from utils.rag import rag_system


class KnowledgeExplainer:
    def __init__(self):
        self.model = hybrid_model_manager
    
    def _validate_generation(self, result: Any) -> Tuple[bool, str, Dict]:
        if not result:
            return False, "生成结果为空", {}
        
        if isinstance(result, str):
            if len(result) < 50:
                return False, f"生成内容过短（{len(result)}字符）", {}
            
            if len(result) > 5000:
                return False, f"生成内容过长（{len(result)}字符）", {}
            
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if not json_match:
                return False, "无法找到JSON格式", {}
            
            try:
                result_data = json.loads(json_match.group())
            except json.JSONDecodeError as e:
                return False, f"JSON解析失败: {e}", {}
            
            if "explanation" not in result_data:
                return False, "缺少explanation字段", {}
            
            if len(result_data["explanation"]) < 50:
                return False, "explanation内容过短", {}
            
            return True, "验证通过", result_data
        
        return False, "未知格式", {}
    
    def generate_explanation(self, knowledge_point: str, mode: str = "simple", use_rag: bool = True, use_search: bool = True, max_retries: int = 2) -> Dict[str, Any]:
        print(f"[讲解师] 讲解: {knowledge_point}, 模式: {mode}")
        
        context = ""
        source_info = ""
        
        if config.ENABLE_RAG and use_rag:
            print(f"[讲解师] 尝试RAG检索...")
            rag_results = rag_system.query(knowledge_point, top_k=3)
            if rag_results:
                context = "\n".join([f"- {doc['content']}" for doc in rag_results])
                source_info = "（来自本地知识库）"
                print(f"[讲解师] RAG找到 {len(rag_results)} 条相关内容")
            else:
                use_search = True
        
        if use_search and not context:
            print(f"[讲解师] RAG没有结果，尝试网络搜索...")
            search_result = web_search_tool(knowledge_point)
            if search_result:
                context = search_result
                source_info = "（来自网络搜索）"
                print(f"[讲解师] 网络搜索成功")
            else:
                context = ""
                source_info = "（来自模型生成）"
        
        if mode in ["deep", "弄清楚"]:
            prompt = f"""请深入讲解以下知识点：

知识点：{knowledge_point}

{'参考资料：' + context if context else ''}

要求：
1. 详细且深入的讲解，包含背景、原理、应用等
2. 提供示例帮助理解
3. 至少500字
4. 同时生成一道针对该讲解的选择题

输出格式（JSON）：
{{
    "explanation": "详细讲解内容",
    "exercise": {{
        "question": "题目内容",
        "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
        "answer": "A",
        "explanation": "答案解析"
    }}
}}"""
        else:
            prompt = f"""请简要讲解以下知识点：

知识点：{knowledge_point}

{'参考资料：' + context if context else ''}

要求：
1. 简洁明了，通俗易懂
2. 突出核心概念
3. 200-300字
4. 同时生成一道针对该讲解的选择题

输出格式（JSON）：
{{
    "explanation": "简洁讲解内容",
    "exercise": {{
        "question": "题目内容",
        "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
        "answer": "A",
        "explanation": "答案解析"
    }}
}}"""
        
        for attempt in range(max_retries + 1):
            print(f"[讲解师] 开始生成讲解+习题 (尝试 {attempt + 1}/{max_retries + 1})...")
            result = self.model.generate_local(prompt)
            
            valid, reason, result_data = self._validate_generation(result)
            
            if valid:
                print(f"[讲解师] 生成成功，自检通过")
                final_explanation = result_data.get("explanation", str(result))
                final_exercise = result_data.get("exercise")
                
                if not final_exercise:
                    final_exercise = self._generate_exercise_fallback(knowledge_point, final_explanation)
                
                return {
                    "knowledge_point": knowledge_point,
                    "explanation": final_explanation + source_info if final_explanation else "暂无讲解内容",
                    "mode": mode,
                    "exercise": final_exercise,
                    "source": "rag" if source_info and "知识库" in source_info else ("web" if "网络搜索" in source_info else "model"),
                    "generation_attempts": attempt + 1,
                    "validation": "passed"
                }
            
            print(f"[讲解师] 自检失败: {reason}")
            if attempt < max_retries:
                print(f"[讲解师] 重试中...")
        
        print(f"[讲解师] 所有尝试均失败，使用后备方案")
        return {
            "knowledge_point": knowledge_point,
            "explanation": f"生成失败，无法获取{knowledge_point}的讲解内容",
            "mode": mode,
            "exercise": self._generate_exercise_fallback(knowledge_point, f"关于{knowledge_point}的讲解"),
            "source": "fallback",
            "generation_attempts": max_retries + 1,
            "validation": "failed",
            "error": "所有生成尝试均失败"
        }
    
    def _generate_exercise_fallback(self, knowledge_point: str, explanation: str) -> Dict[str, Any]:
        print(f"[讲解师] 使用后备方案生成习题...")
        prompt = f"""基于以下知识点生成一道选择题：

知识点：{knowledge_point}
讲解内容：{explanation}

要求：
1. 题目难度适中，针对知识点核心内容
2. 4个选项必须清晰明确
3. 有且只有一个正确答案
4. 提供详细的答案解析

输出格式（JSON）：
{{
    "question": "题目内容",
    "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
    "answer": "A",
    "explanation": "详细解析"
}}"""

        result = self.model.generate_local(prompt)
        
        try:
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"[讲解师] 后备方案也失败: {e}")
        
        return {
            "question": f"以下关于'{knowledge_point}'的说法正确的是？",
            "options": [
                "A. 这是第一个正确说法",
                "B. 这是第二个说法",
                "C. 这是第三个说法",
                "D. 以上都不对"
            ],
            "answer": "A",
            "explanation": f"'{knowledge_point}'是重要概念，需要深入理解。"
        }
    
    def format_explanation(self, explanation_data: Dict[str, Any]) -> str:
        output = []
        output.append("="*60)
        output.append(f"📚 知识点：{explanation_data.get('knowledge_point', '')}")
        output.append("="*60)
        output.append("")
        output.append(explanation_data.get('explanation', ''))
        return "\n".join(output)


explainer = KnowledgeExplainer()