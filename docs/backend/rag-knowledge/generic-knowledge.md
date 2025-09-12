# `rag_knowledge/generic_knowledge.py` - 通用 RAG 知识处理

本文档描述了 `backend/app/rag_knowledge/generic_knowledge.py` 文件，该文件包含了处理 RAG（Retrieval-Augmented Generation）知识的通用逻辑，包括文档处理、Milvus 搜索和与 LLM 的交互。

## 功能描述
*   **文档处理**: 将原始文档（如 Markdown 文件）处理成可用于 RAG 的文本块（chunks）。
*   **Milvus 搜索**: 根据用户查询在 Milvus 向量数据库中执行相似度搜索，检索相关文档块。
*   **LLM 交互**: 将检索到的文档块作为上下文提供给大语言模型（LLM），以生成增强的响应。
*   **文件元数据处理**: 提取和管理文档的元数据，如文件名、下载 URL 和摘要。

## 逻辑实现
1.  **`process_markdown_file(file_path: str, filename: str, user_id: int, db: Session)`**:
    *   读取 Markdown 文件内容。
    *   将文件内容分割成多个文本块（chunks）。
    *   为每个文本块生成嵌入（使用 `embedding_service`）。
    *   将文本块、嵌入、文件名、文件路径、摘要等信息存储到 Milvus 和 MongoDB。
    *   更新 `FileGist` 数据库记录。
2.  **`search_in_milvus(query: str, top_k: int = 5)`**:
    *   为用户查询生成嵌入。
    *   在 Milvus 中执行向量相似度搜索，检索与查询最相关的 `top_k` 个文档块。
    *   返回包含文档内容、元数据（如文件名、下载 URL、摘要）的 `Document` 对象列表。
3.  **`query_rag_system(query: str, db_session: Session)`**:
    *   这是 RAG 系统的核心函数。
    *   首先调用 `search_in_milvus` 检索相关文档。
    *   然后，从 MongoDB 获取这些文档的摘要和原始块内容（通过 `rag_file_service`）。
    *   构建一个包含检索到的信息（文件名、下载 URL、摘要、相关块）的上下文。
    *   将此上下文与用户查询一起传递给 LLM（通过 `backend.app.llm.chain` 中的函数），指导 LLM 使用这些信息生成响应，并以 Markdown 格式包含可点击的下载链接。

## 路径
`/backend/app/rag_knowledge/generic_knowledge.py`