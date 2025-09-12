# `routers/embeddings.py` - 嵌入路由

本文档描述了 `backend/app/routers/embeddings.py` 文件，该文件定义了与文本嵌入生成相关的 API 路由。

## 功能描述
*   **生成文本嵌入**: 提供一个接口，允许客户端请求为给定的文本生成向量嵌入。

## 逻辑实现
1.  **`create_embedding(text: str)`**:
    *   接收要生成嵌入的文本。
    *   调用 `rag_knowledge.embedding_service.get_text_embedding` 来生成文本嵌入。
    *   返回生成的嵌入向量。
    *   `@router.post("/embeddings")`

## 路径
`/backend/app/routers/embeddings.py`