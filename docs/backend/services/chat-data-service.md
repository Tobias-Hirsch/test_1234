# `services/chat_data_service.py` - 聊天数据服务

本文档描述了 `backend/app/services/chat_data_service.py` 文件，该文件包含了与聊天消息和会话数据存储和检索相关的业务逻辑。

## 功能描述
*   **消息存储**: 将聊天消息（用户和代理的）保存到数据库。
*   **会话管理**: 创建和管理聊天会话。
*   **历史检索**: 检索特定会话的聊天历史。
*   **数据结构化**: 确保聊天数据以一致的结构存储。

## 逻辑实现
该模块主要与 MongoDB 数据库进行交互，存储聊天消息和会话元数据。

1.  **`save_message(conversation_id: str, message_content: str, is_user: bool, source_documents: Optional[List[dict]] = None)`**:
    *   将单条聊天消息保存到 MongoDB 的 `messages` 集合中。
    *   消息包含 `conversation_id`、`content`、`is_user`、`timestamp` 和可选的 `source_documents`。
2.  **`get_conversation_messages(conversation_id: str) -> List[dict]`**:
    *   根据 `conversation_id` 从 `messages` 集合中检索所有消息。
    *   按时间戳排序并返回。
3.  **`create_conversation(user_id: int) -> str`**:
    *   在 MongoDB 的 `conversations` 集合中创建一个新的会话记录。
    *   返回新生成的 `conversation_id`。

## 路径
`/backend/app/services/chat_data_service.py`