# `llm/chain.py` - LLM Chains and Business Logic

This document describes the `backend/app/llm/chain.py` file, which contains the business logic for interacting with Large Language Models (LLMs), specifically for building and executing LLM chains to complete specific tasks, such as legal summarization.

## Function Description
*   **LLM Instantiation**: Initializes and configures the LLM client (e.g., OpenAI, Ollama).
*   **Prompt Engineering**: Constructs system prompts and user prompts to guide LLM behavior.
*   **Chained Calls**: Combines multiple LLM calls or tool uses into a logical chain to complete complex tasks.
*   **Task-Specific Logic**: Contains customized logic for specific LLM tasks (e.g., summarization, Q&A).

## Logic Implementation
This module will use LangChain or custom implementations to build LLM chains.

For example, an asynchronous function for legal summarization:
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
    llm = get_llm_client() # Get LLM client

    system_prompt = "You are a professional legal summarization assistant. Please generate a concise and accurate summary based on the provided legal text."
    if query:
        system_prompt += f" Please pay special attention to content related to the following question: '{query}'."

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Please summarize the following legal text:\n\n{text}"}
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

## Path
`/backend/app/llm/chain.py`