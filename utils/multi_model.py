from openai import OpenAI
import os

class MultiModelManager:
    """多模型管理器，支持模型协作"""

    def __init__(self):
        self.base_url = "http://localhost:11434/v1"
        self.api_key = "ollama"

        self.models = {
            "primary": {
                "name": "qwen2.5:7b",
                "description": "主模型 - 深度理解和复杂任务",
                "strengths": ["深度讲解", "复杂概念", "项目实战", "面试准备"],
                "context_window": 8192,
                "memory_usage": "5GB"
            },
            "secondary": {
                "name": "qwen3:4b",
                "description": "辅助模型 - 快速响应和简单任务",
                "strengths": ["快速响应", "简单查询", "概念解释", "基础问答"],
                "context_window": 8192,
                "memory_usage": "3GB"
            }
        }

        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )

        print(f"[MultiModel] 初始化完成")
        print(f"[MultiModel] 主模型: {self.models['primary']['name']}")
        print(f"[MultiModel] 辅助模型: {self.models['secondary']['name']}")

    def get_model(self, task_type: str) -> str:
        """根据任务类型选择合适的模型"""
        if task_type in ["deep_explanation", "complex_analysis", "interview_prep", "project_practice"]:
            return self.models["primary"]["name"]
        elif task_type in ["simple_explanation", "quick_query", "basic_qa", "concept_intro"]:
            return self.models["secondary"]["name"]
        else:
            return self.models["primary"]["name"]

    def generate_content(self, task_type: str, prompt: str, **kwargs) -> str:
        """生成内容，自动选择合适的模型"""
        model = self.get_model(task_type)

        print(f"[MultiModel] 任务类型: {task_type}")
        print(f"[MultiModel] 使用模型: {model}")

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2000),
                stream=True
            )

            content = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content += chunk.choices[0].delta.content

            return content

        except Exception as e:
            print(f"[MultiModel] 生成失败: {e}")
            fallback_model = self.models["secondary"]["name"]
            print(f"[MultiModel] 尝试备用模型: {fallback_model}")

            try:
                response = self.client.chat.completions.create(
                    model=fallback_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=2000
                )
                return response.choices[0].message.content
            except:
                return self._generate_mock_response(prompt)

    def parallel_generate(self, prompts: list, model: str = None) -> list:
        """并行生成多个内容"""
        results = []
        for prompt in prompts:
            model_name = model or self.models["primary"]["name"]
            result = self.client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            results.append(result.choices[0].message.content)
        return results

    def collaborative_generate(self, task: str, context: dict) -> dict:
        """协作生成 - 多个模型协同工作"""
        results = {
            "quick_summary": None,
            "deep_analysis": None,
            "related_concepts": None,
            "exercises": None
        }

        quick_prompt = f"简洁概括以下内容：{task}\n\n{context.get('knowledge_point', '')}"
        results["quick_summary"] = self.generate_content(
            "simple_explanation",
            quick_prompt
        )

        deep_prompt = f"""深度分析以下知识点：

{task}
知识点：{context.get('knowledge_point', '')}

请详细讲解：
1. 核心概念与原理
2. 技术实现细节
3. 项目实战经验
4. 常见问题与解决方案
"""
        results["deep_analysis"] = self.generate_content(
            "deep_explanation",
            deep_prompt,
            max_tokens=3000
        )

        concepts_prompt = f"为以下知识点生成5个相关联的概念：{context.get('knowledge_point', '')}"
        results["related_concepts"] = self.generate_content(
            "complex_analysis",
            concepts_prompt
        )

        exercises_prompt = f"""基于以下知识点生成4道高质量习题：

知识点：{context.get('knowledge_point', '')}
学习目标：{context.get('learning_goal', '深入理解')}

请生成：
1. 选择题（考察核心概念）
2. 简答题（考察原理理解）
3. 实践题（考察应用能力）
4. 综合题（考察融会贯通）
"""
        results["exercises"] = self.generate_content(
            "project_practice",
            exercises_prompt,
            max_tokens=2500
        )

        return results

    def _generate_mock_response(self, prompt: str) -> str:
        """模拟响应（当所有模型都失败时）"""
        return f"关于'{prompt}'的详细讲解内容。请稍后重试或检查系统配置。"

multi_model_manager = MultiModelManager()
