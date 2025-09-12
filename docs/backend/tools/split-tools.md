# `tools/split_tools.py` - 文本分割工具

本文档描述了 `backend/app/tools/split_tools.py` 文件，该文件包含了用于将长文本分割成更小、更易于管理和处理的文本块（chunks）的工具函数。这对于 RAG（Retrieval-Augmented Generation）系统尤其重要，因为 LLM 通常有输入长度限制。

## 功能描述
*   **文本分块**: 根据指定的大小和重叠度将文本分割成块。
*   **多种分割策略**: 可能支持不同的分割策略，如按字符、按段落、按句子等。
*   **元数据保留**: 在分割过程中保留或生成与文本块相关的元数据（如原始文档来源、页码）。

## 逻辑实现
该模块通常会使用 LangChain 的 `RecursiveCharacterTextSplitter` 或自定义逻辑来实现文本分割。

例如，一个基于字符的递归文本分割器：
```python
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger(__name__)

def split_text_into_chunks(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Splits a given text into smaller chunks.

    Args:
        text (str): The input text to be split.
        chunk_size (int): The maximum size of each chunk.
        chunk_overlap (int): The number of characters to overlap between chunks.

    Returns:
        List[str]: A list of text chunks.
    """
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            add_start_index=True # 可选：添加每个块在原始文本中的起始索引
        )
        chunks = text_splitter.split_text(text)
        logger.info(f"Text split into {len(chunks)} chunks with size {chunk_size} and overlap {chunk_overlap}.")
        return chunks
    except Exception as e:
        logger.error(f"Error splitting text into chunks: {e}")
        raise

# 示例用法：
# long_text = "这是一个非常长的文本，需要被分割成小块以便处理。每个小块可以有重叠部分，以保留上下文信息。"
# chunks = split_text_into_chunks(long_text, chunk_size=50, chunk_overlap=10)
# for i, chunk in enumerate(chunks):
#     print(f"Chunk {i+1}: {chunk}")
```

## 路径
`/backend/app/tools/split_tools.py`