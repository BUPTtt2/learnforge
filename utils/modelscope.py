import os
import sys
from openai import OpenAI
from config_loader import config

class ModelScopeClient:
    """ModelScope DeepSeek-V3.2 客户端"""

    def __init__(self):
        self.base_url = config.MODELSCOPE_BASE_URL
        self.api_key = config.MODELSCOPE_API_KEY
        self.model = "deepseek-ai/DeepSeek-V3.2"

        if not self.api_key:
            print("[Warning] ModelScope API Key 未配置")
            self.client = None
        else:
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key
            )
            print(f"[Success] ModelScope client initialized")
            print(f"[ModelScope] Model: {self.model}")

    def generate(self, prompt: str, enable_thinking: bool = True, **kwargs) -> dict:
        """
        生成内容

        Args:
            prompt: 输入提示词
            enable_thinking: 是否启用思考模式
            **kwargs: 其他参数

        Returns:
            dict: 包含 reasoning_content 和 content
        """
        if not self.client:
            return self._mock_response(prompt)

        try:
            extra_body = {
                "enable_thinking": enable_thinking
            }

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                stream=True,
                extra_body=extra_body,
                **kwargs
            )

            reasoning_content = ""
            content = ""
            done_thinking = False

            for chunk in response:
                if chunk.choices:
                    thinking_chunk = chunk.choices[0].delta.reasoning_content
                    answer_chunk = chunk.choices[0].delta.content

                    if thinking_chunk:
                        reasoning_content += thinking_chunk
                    elif answer_chunk:
                        if not done_thinking and reasoning_content:
                            done_thinking = True
                        content += answer_chunk

            return {
                "reasoning_content": reasoning_content,
                "content": content,
                "success": True
            }

        except Exception as e:
            print(f"[Error] ModelScope API call failed: {e}")
            return self._mock_response(prompt)

    def _mock_response(self, prompt: str) -> dict:
        """模拟响应（当API不可用时）"""
        return {
            "reasoning_content": "",
            "content": f"关于'{prompt}'的详细讲解内容。",
            "success": False
        }

    def plan_content(self, topic: str, learning_goal: str = "") -> dict:
        """
        使用高质量推理能力规划内容

        Args:
            topic: 学习主题
            learning_goal: 学习目标

        Returns:
            dict: 包含规划结果
        """
        prompt = f"""你是一个专业的学习规划专家。请为用户规划以下主题的学习内容：

主题：{topic}
学习目标：{learning_goal if learning_goal else "深入理解"}

请按以下格式规划：

## 学习目标
[描述学习目标]

## Part 划分
将内容划分为多个Part，每个Part包含若干章节：

### Part 1: [Part名称]
- 章节1.1: [章节名称]
- 章节1.2: [章节名称]
...

### Part 2: [Part名称]
- 章节2.1: [章节名称]
...

## 每个Part的概述
[简要描述每个Part的核心内容]

## 学习建议
[学习顺序建议、时间安排等]
"""
        return self.generate(prompt, enable_thinking=True)

    def analyze_complexity(self, topic: str) -> dict:
        """
        分析知识点复杂度

        Args:
            topic: 知识点

        Returns:
            dict: 包含复杂度分析
        """
        prompt = f"""请分析以下知识点的复杂度：

{topic}

请从以下维度分析：
1. 概念难度（1-5）
2. 需要的前置知识
3. 预计学习时长
4. 适合的学习模式（简单了解/深度理解）
5. 相关知识点

请用简洁的语言回答。"""

        result = self.generate(prompt, enable_thinking=False)
        return {
            "analysis": result.get("content", ""),
            "success": result.get("success", False)
        }

# 全局实例
modelscope_client = ModelScopeClient()
