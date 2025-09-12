# `routers/chat.py` - 聊天路由

本文档描述了 `backend/app/routers/chat.py` 文件，该文件定义了与聊天功能相关的 API 路由。

## 功能描述
*   **发送聊天消息**: 提供用户发送消息到聊天系统的接口。
*   **获取聊天历史**: 提供获取特定会话聊天历史的接口。
*   **创建新会话**: 提供创建新聊天会话的接口。
*   **RAG 集成**: 在聊天消息处理中集成 RAG（Retrieval-Augmented Generation）功能，根据用户查询从知识库中检索信息并增强 LLM 响应。
*   **LLM 交互**: 与大语言模型（LLM）进行交互，生成聊天回复。

## 逻辑实现
1.  **`add_conversation_message(message: schemas.AgentChatRequest, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_active_user))`**:
    *   接收用户发送的聊天消息。
    *   如果启用了 RAG (`AGENTIC_RAG_ENABLE=False` 时的直接聊天路径)，则调用 `rag_knowledge.generic_knowledge.query_rag_system` 来检索相关文档和摘要。
    *   构建 LLM 的系统提示，将检索到的 RAG 信息（包括文件名、下载 URL、摘要）作为上下文传递给 LLM。
    *   调用 LLM（通过 `backend.app.llm.chain` 中的函数）生成回复。
    *   将用户消息和 LLM 回复保存到数据库（MongoDB）。
    *   返回 LLM 生成的回复。
    *   `@router.post("/add_conversation_message")`
2.  **`get_conversation_history(conversation_id: str, current_user: User = Depends(auth.get_current_active_user))`**:
    *   根据 `conversation_id` 从 MongoDB 中检索聊天历史。
    *   返回聊天消息列表。
    *   `@router.get("/history/{conversation_id}")`
3.  **`create_new_conversation(current_user: User = Depends(auth.get_current_active_user))`**:
    *   为当前用户创建一个新的聊天会话。
    *   返回新会话的 ID。
    *   `@router.post("/new_conversation")`

## 路径
`/backend/app/routers/chat.py`