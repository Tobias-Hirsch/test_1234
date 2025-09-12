# `routers/agent_chat.py` - 代理聊天路由

本文档描述了 `backend/app/routers/agent_chat.py` 文件，该文件定义了与多代理（Agentic）聊天功能相关的 API 路由。

## 功能描述
*   **代理聊天消息**: 提供用户与多代理系统进行交互的接口。
*   **工作流编排**: 当 `AGENTIC_RAG_ENABLE=TRUE` 时，此路由负责编排不同代理（如信息检索代理、代码生成代理、文件处理代理等）的工作流，以响应用户查询。
*   **工具使用**: 代理可能在此过程中调用各种工具来完成任务。

## 逻辑实现
1.  **`add_agent_conversation_message(message: schemas.AgentChatRequest, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_active_user))`**:
    *   接收用户发送的聊天消息。
    *   根据 `AGENTIC_RAG_ENABLE` 配置，如果为 `True`，则激活多代理工作流。
    *   **编排逻辑**:
        *   `orchestrator_agent` 接收用户查询，并决定需要激活哪些子代理来处理请求。
        *   `information_retrieval_agent` 用于从知识库中检索信息。
        *   `code_generation_agent` 用于生成代码。
        *   `file_processing_agent` 用于处理文件。
        *   `reasoning_planning_agent` 用于复杂的推理和规划。
        *   `validation_agent` 用于验证结果。
        *   `formatting_output_agent` 用于格式化最终输出。
    *   代理之间通过内部消息传递和状态管理进行协作。
    *   将代理生成的回复保存到数据库（MongoDB）。
    *   返回代理生成的回复。
    *   `@router.post("/add_agent_conversation_message")`

## 路径
`/backend/app/routers/agent_chat.py`