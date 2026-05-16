import os
from dotenv import load_dotenv

load_dotenv()

# 火山引擎API配置 - 敏感信息请在.env文件中设置
VOLCENGINE_API_KEY = os.getenv("VOLCENGINE_API_KEY", "")
VOLCENGINE_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
DEEPSEEK_MODEL = "deepseek-v3-2-251201"

# ModelScope配置（备用）- 敏感信息请在.env文件中设置
MODELSCOPE_API_TOKEN = os.getenv("MODELSCOPE_API_TOKEN", "")

PROJECT_NAME = "LearnForge"
VERSION = "1.0.0"

MEMORY_DB_PATH = "./memory_db"

LEARNING_MODES = {
    "simple": "简单了解",
    "deep": "弄清楚"
}

COMPLEXITY_THRESHOLD = 0.5
MAX_CACHE_SIZE = 1000
API_CALL_DELAY = 0.5