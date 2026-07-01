import os
import posthog
from dotenv import load_dotenv
from zhipuai import ZhipuAI

# 第一时间屏蔽chromadb遥测报错，避免日志噪音
posthog.capture = lambda *args, **kwargs: None

load_dotenv()

ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
DEFAULT_MODEL = "glm-5.2"
EMBEDDING_MODEL = "embedding-3"

client = ZhipuAI(api_key=ZHIPU_API_KEY)