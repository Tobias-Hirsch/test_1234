# `services/ollama_service.py` - Ollama 通用服务

本文档描述了 `backend/app/services/ollama_service.py` 文件，该文件可能提供了与 Ollama 服务进行通用交互的业务逻辑，不限于特定模型。

## 功能描述
*   **Ollama API 封装**: 封装了 Ollama REST API 的通用调用，如列出模型、拉取模型、删除模型等。
*   **健康检查**: 检查 Ollama 服务是否可用。
*   **通用文本/聊天接口**: 提供与 Ollama 上任何模型进行文本生成或聊天补全的通用接口。

## 逻辑实现
该模块会直接或间接使用 `ollama_module.py` 中的低级 HTTP 客户端，并提供更高级别的业务逻辑。

例如，一个通用的 Ollama 聊天服务：
```python
import httpx
from backend.app.core.config import settings
from backend.app.modules.ollama_module import OLLAMA_BASE_URL
import logging

logger = logging.getLogger(__name__)

async def get_ollama_models() -> list[dict]:
    """Lists available models from Ollama service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            response.raise_for_status()
            return response.json().get("models", [])
    except httpx.RequestError as e:
        logger.error(f"Error connecting to Ollama service to list models: {e}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred while listing Ollama models: {e}")
        return []

async def chat_with_ollama(messages: list[dict], model_name: str) -> str:
    """
    Interacts with a specified Ollama model for chat completions.
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
        logger.error(f"Error connecting to Ollama service for chat: {e}")
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama chat service returned an error: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during Ollama chat: {e}")
        raise
```

## 路径
`/backend/app/services/ollama_service.py`