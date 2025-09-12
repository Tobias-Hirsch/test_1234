# API 接口

本节列出了 Rosti 后端提供的主要 RESTful API 接口及其功能。

## 1. 认证与用户管理

*   **`/auth/login`**: 用户登录，获取认证令牌。
*   **`/auth/register`**: 新用户注册。
*   **`/users/me`**: 获取当前用户信息。

## 2. 聊天功能

*   **`/chat/conversations`**: 获取用户会话列表，创建新会话。
*   **`/chat/conversations/{conversation_id}/messages`**: 获取会话消息，添加新消息。
*   **`/chat/upload_files`**: 上传聊天附件。
*   **`/chat/conversations/{conversation_id}/messages/{message_id}/attachments/{attachment_id}/download`**: 下载聊天附件。

## 3. 知识库 (RAG) 管理

*   **`/rag/items`**: 获取知识库条目列表，创建新条目。
*   **`/rag/items/{rag_id}/files`**: 获取知识库条目下的文件列表，上传新文件。
*   **`/rag/items/{rag_id}/files/{file_id}/download`**: 下载知识库文件。

## 4. 工具与服务

*   **`/tools/search`**: 在线搜索工具接口。
*   **`/tools/pdf-process`**: PDF 处理工具接口。

## 5. 数据模型

*   **`User`**: 用户数据模型。
*   **`Conversation`**: 会话数据模型。
*   **`Message`**: 消息数据模型，包含附件信息。
*   **`Attachment`**: 附件数据模型，包含 MinIO 存储信息。
*   **`RagItem`**: 知识库条目数据模型。
*   **`FileGist`**: 知识库文件元数据模型。

每个接口都支持 JSON 请求和响应，并遵循 RESTful 设计原则。