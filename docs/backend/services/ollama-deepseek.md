# `services/ollama_deepseek.py` - Ollama DeepSeek 集成服务

本文档描述了 `backend/app/services/ollama_deepseek.py` 文件，该文件可能专门用于与本地 Ollama 服务上部署的 DeepSeek 模型进行交互。

## 功能描述
*   **DeepSeek 模型调用**: 封装了调用 Ollama 上 DeepSeek 模型进行文本生成或聊天补全的功能。
*   **特定模型配置**: 可能包含针对 DeepSeek 模型优化的参数设置。

## 逻辑实现
该模块会利用 `ollama_module.py` 中定义的通用 Ollama 交互函数，并可能添加 DeepSeek 模型特有的处理逻辑或参数。

例如，一个使用 DeepSeek 模型进行聊天的示例：
```python
import httpx
from backend.app.core.config import settings
from backend.app.modules.ollama_module import OLLAMA_BASE_URL
import logging

logger = logging.getLogger(__name__)

async def chat_with_ollama_deepseek(messages: list[dict], model_name: str = "deepseek-coder") -> str:
    """
    Interacts with the DeepSeek model via Ollama for chat completions.
    Messages should be in the format: [{"role": "user", "content": "..."}]
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": model_name,
                    "messages": messages,
                    "stream": False
                },
                timeout=600.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
    except httpx.RequestError as e:
        logger.error(f"Error connecting to Ollama DeepSeek service: {e}")
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama DeepSeek service returned an error: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during Ollama DeepSeek chat: {e}")
        raise
```

## 路径
`/backend/app/services/ollama_deepseek.py`