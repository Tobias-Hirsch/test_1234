# `llm/llm.py` - LLM 客户端管理

本文档描述了 `backend/app/llm/llm.py` 文件，该文件负责初始化和管理大语言模型（LLM）客户端，根据配置选择不同的 LLM 提供商。

## 功能描述
*   **LLM 客户端实例化**: 根据环境变量配置（如 OpenAI API 密钥或 Ollama URL），实例化相应的 LLM 客户端。
*   **统一接口**: 提供一个统一的函数来获取 LLM 客户端实例，方便其他模块调用。
*   **模型选择**: 支持根据配置选择不同的 LLM 模型。

## 逻辑实现
该模块会检查环境变量，并根据检测到的配置返回相应的 LLM 客户端。

例如，选择 OpenAI 或 Ollama 客户端：
```python
import os
from backend.app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# 缓存LLM客户端实例
_llm_client = None

def get_llm_client():
    """
    Returns an initialized LLM client based on configuration.
    Supports OpenAI and Ollama.
    """
    global _llm_client
    if _llm_client:
        return _llm_client

    if settings.OPENAI_API_KEY:
        try:
            from openai import OpenAI
            _llm_client = OpenAI(api_key=settings.OPENAI_API_KEY)
            _llm_client.model = os.getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo") # 默认模型
            logger.info(f"Initialized OpenAI LLM client with model: {_llm_client.model}")
            return _llm_client
        except ImportError:
            logger.error("OpenAI library not found. Please install it: pip install openai")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI LLM client: {e}")
            raise
    elif settings.OLLAMA_BASE_URL and settings.OLLAMA_CHAT_MODEL:
        try:
            from openai import OpenAI # Ollama兼容OpenAI API
            _llm_client = OpenAI(
                base_url=settings.OLLAMA_BASE_URL,
                api_key="ollama" # Ollama API key is typically not required or can be a placeholder
            )
            _llm_client.model = settings.OLLAMA_CHAT_MODEL
            logger.info(f"Initialized Ollama LLM client with base URL: {settings.OLLAMA_BASE_URL} and model: {_llm_client.model}")
            return _llm_client
        except ImportError:
            logger.error("OpenAI library not found. Please install it: pip install openai (required for Ollama compatibility)")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Ollama LLM client: {e}")
            raise
    else:
        raise ValueError("No LLM provider configured. Please set OPENAI_API_KEY or OLLAMA_BASE_URL/OLLAMA_CHAT_MODEL.")

```

## 路径
`/backend/app/llm/llm.py`