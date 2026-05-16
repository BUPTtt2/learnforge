import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

class Config:
    # ==================== 云端API配置 ====================
    MODELSCOPE_API_KEY = os.getenv("MODELSCOPE_API_KEY", "")
    MODELSCOPE_BASE_URL = os.getenv("MODELSCOPE_BASE_URL", "https://api-inference.modelscope.cn/v1")

    BAIDU_CLOUD_API_KEY = os.getenv("BAIDU_CLOUD_API_KEY", "")

    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

    # ==================== 外部搜索配置 ====================
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

    # ==================== 本地模型配置 ====================
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "ollama")

    DEFAULT_LOCAL_MODEL = os.getenv("DEFAULT_LOCAL_MODEL", "qwen2.5:7b")
    FAST_LOCAL_MODEL = os.getenv("FAST_LOCAL_MODEL", "qwen3:4b")

    # ==================== 应用配置 ====================
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # ==================== 功能开关 ====================
    ENABLE_CLOUD_MODEL = os.getenv("ENABLE_CLOUD_MODEL", "True").lower() == "true"
    ENABLE_RAG = os.getenv("ENABLE_RAG", "False").lower() == "true"
    ENABLE_MULTIMODAL = os.getenv("ENABLE_MULTIMODAL", "True").lower() == "true"
    ENABLE_ASYNC = os.getenv("ENABLE_ASYNC", "True").lower() == "true"

    # ==================== 模型分配策略 ====================
    @classmethod
    def get_model_for_task(cls, task_type: str) -> dict:
        """
        根据任务类型获取合适的模型配置

        Args:
            task_type: 任务类型
                - "planning": 内容规划/Part拆分 (使用云端高质量模型)
                - "search": 外部搜索 (使用百度云)
                - "tavily_search": 外部搜索 (使用Tavily AI)
                - "generation": 学习内容生成 (使用本地模型)
                - "exercises": 习题生成 (使用本地快速模型)
                - "multimodal": 语音处理 (使用本地Whisper/gTTS)

        Returns:
            dict: 包含 model, base_url, api_key, model_name
        """
        strategies = {
            "planning": {
                "model": "deepseek-ai/DeepSeek-V3.2",
                "base_url": cls.MODELSCOPE_BASE_URL,
                "api_key": cls.MODELSCOPE_API_KEY,
                "model_name": "DeepSeek-V3.2",
                "description": "高质量推理能力，用于内容规划"
            },
            "search": {
                "model": "baidu_search",
                "base_url": "https://qianfan.baidubce.com/v2/ai_search",
                "api_key": cls.BAIDU_CLOUD_API_KEY,
                "model_name": "Baidu Cloud Search",
                "description": "用于外部搜索增强"
            },
            "tavily_search": {
                "model": "tavily_ai",
                "base_url": "https://api.tavily.com",
                "api_key": cls.TAVILY_API_KEY,
                "model_name": "Tavily AI",
                "description": "用于RAG外部搜索"
            },
            "generation": {
                "model": cls.DEFAULT_LOCAL_MODEL,
                "base_url": cls.OLLAMA_BASE_URL,
                "api_key": cls.OLLAMA_API_KEY,
                "model_name": cls.DEFAULT_LOCAL_MODEL,
                "description": "免费快速，用于学习内容生成"
            },
            "exercises": {
                "model": cls.FAST_LOCAL_MODEL,
                "base_url": cls.OLLAMA_BASE_URL,
                "api_key": cls.OLLAMA_API_KEY,
                "model_name": cls.FAST_LOCAL_MODEL,
                "description": "轻量快速，用于习题生成"
            },
            "fallback": {
                "model": "qwen2.5:7b",
                "base_url": cls.OLLAMA_BASE_URL,
                "api_key": cls.OLLAMA_API_KEY,
                "model_name": "Qwen2.5-7B",
                "description": "备用模型"
            }
        }

        return strategies.get(task_type, strategies["fallback"])

    @classmethod
    def is_cloud_available(cls) -> bool:
        """检查云端模型是否可用"""
        return cls.ENABLE_CLOUD_MODEL and bool(cls.MODELSCOPE_API_KEY)

    @classmethod
    def is_search_available(cls) -> bool:
        """检查搜索功能是否可用"""
        return bool(cls.BAIDU_CLOUD_API_KEY)

    @classmethod
    def is_tavily_available(cls) -> bool:
        """检查Tavily AI是否可用"""
        return bool(cls.TAVILY_API_KEY)

config = Config()
