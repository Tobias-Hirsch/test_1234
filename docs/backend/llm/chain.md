# `llm/chain.py` - LLM 链与业务逻辑

本文档描述了 `backend/app/llm/chain.py` 文件，该文件包含了与大语言模型（LLM）交互的业务逻辑，特别是用于构建和执行 LLM 链，以完成特定任务，如法律摘要。

## 功能描述
*   **LLM 实例化**: 初始化并配置 LLM 客户端（如 OpenAI、Ollama）。
*   **提示工程**: 构建用于指导 LLM 行为的系统提示和用户提示。
*   **链式调用**: 将多个 LLM 调用或工具使用组合成一个逻辑链，以完成复杂任务。
*   **任务特定逻辑**: 包含针对特定 LLM 任务（如摘要、问答）的定制逻辑。

## 逻辑实现
该模块会使用 LangChain 或自定义实现来构建 LLM 链。

例如，一个用于法律摘要的异步函数：
```python
from typing import Optional
from backend.app.llm.llm import get_llm_client
import logging

logger = logging.getLogger(__name__)

async def fn_async_summarize_law(text: str, query: Optional[str] = None) -> str:
    """
    Asynchronously summarizes legal text using an LLM.
    Optionally takes a query to focus the summary.
    """
    llm = get_llm_client() # 获取LLM客户端

    system_prompt = "你是一个专业的法律摘要助手。请根据提供的法律文本，生成一个简洁、准确的摘要。"
    if query:
        system_prompt += f"请特别关注与以下问题相关的内容：'{query}'。"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"请摘要以下法律文本：\n\n{text}"}
    ]

    try:
        response = await llm.chat.completions.create(
            model=llm.model,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error summarizing law with LLM: {e}")
        raise
```

## 路径
`/backend/app/llm/chain.py`