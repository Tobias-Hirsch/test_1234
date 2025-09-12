# `modules/ollama_module.py` - Ollama 模块

本文档描述了 `backend/app/modules/ollama_module.py` 文件，该文件可能用于与本地运行的 Ollama 服务进行交互，以使用本地大语言模型。

## 功能描述
*   **Ollama 连接**: 提供与 Ollama 服务建立连接的功能。
*   **模型管理**: 可能包含列出可用模型、下载模型等功能。
*   **文本生成**: 通过 Ollama 服务调用本地模型进行文本生成。
*   **嵌入生成**: 通过 Ollama 服务生成文本嵌入。

## 逻辑实现
该模块通常会使用 `httpx` 或 `requests` 库与 Ollama 的 REST API 进行通信。

例如，一个简单的 Ollama 文本生成示例：
```python
import httpx
from backend.app.core.config import settings
import logging

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

async def generate_text_with_ollama(model_name: str, prompt: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=600.0 # 增加超时时间
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
    except httpx.RequestError as e:
        logger.error(f"Error connecting to Ollama service: {e}")
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama service returned an error: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during Ollama text generation: {e}")
        raise

async def generate_embedding_with_ollama(model_name: str, text: str) -> list[float]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/embeddings",
                json={
                    "model": model_name,
                    "prompt": text
                },
                timeout=600.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("embedding", [])
    except httpx.RequestError as e:
        logger.error(f"Error connecting to Ollama service for embedding: {e}")
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama embedding service returned an error: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during Ollama embedding generation: {e}")
        raise
```

## 路径
`/backend/app/modules/ollama_module.py`