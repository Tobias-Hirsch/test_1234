# `services/conversation_cleaner.py` - 会话清理服务

本文档描述了 `backend/app/services/conversation_cleaner.py` 文件，该文件包含了定期清理旧聊天会话的业务逻辑。

## 功能描述
*   **定期清理**: 自动删除超过指定保留期限的聊天会话。
*   **数据维护**: 帮助管理数据库大小，提高查询效率，并遵守数据保留策略。

## 逻辑实现
1.  **`remove_old_conversations()`**:
    *   从 `backend.app.core.config` 中获取 `CONVERSATION_CLEANUP_DAYS` 配置，确定会话的保留天数。
    *   计算出需要删除的会话的截止日期。
    *   连接到 MongoDB 数据库。
    *   在 `conversations` 集合中查找并删除所有创建时间早于截止日期的会话。
    *   记录清理操作的日志。

## 路径
`/backend/app/services/conversation_cleaner.py`