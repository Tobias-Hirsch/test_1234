# `schemas/chat_schemas.py` - 聊天数据模式

本文档描述了 `backend/app/schemas/chat_schemas.py` 文件，该文件专门定义了与聊天功能相关的数据模式（Schema）。

## 功能描述
*   **聊天请求**: 定义用户发送聊天消息的请求体结构。
*   **聊天响应**: 定义聊天系统返回的响应体结构，包括消息内容、会话 ID、消息 ID、时间戳等。
*   **RAG 源文档**: 定义 RAG 功能中检索到的源文档的结构，包括文件名、下载 URL 和摘要。

## 逻辑实现
该文件通常包含继承自 `pydantic.BaseModel` 的类，用于定义聊天相关的输入和输出数据结构。

例如，可能包含以下模式：
*   **`AgentChatRequest`**:
    ```python
    from typing import Optional, List
    from pydantic import BaseModel, Field
    from datetime import datetime

    class AgentChatRequest(BaseModel):
        message: str = Field(..., description="The user's message to the chat agent.")
        conversation_id: Optional[str] = Field(None, description="Optional ID of the ongoing conversation.")
    ```
*   **`SourceDocument`**:
    ```python
    class SourceDocument(BaseModel):
        filename: str = Field(..., description="The name of the source file.")
        download_url: Optional[str] = Field(None, description="Pre-signed URL to download the source file.")
        summary: Optional[str] = Field(None, description="A summary of the relevant content from the source document.")
        chunk_content: Optional[str] = Field(None, description="The specific chunk content from the source document.")
    ```
*   **`AgentChatResponse`**:
    ```python
    class AgentChatResponse(BaseModel):
        response: str = Field(..., description="The agent's response message.")
        conversation_id: str = Field(..., description="The ID of the conversation.")
        message_id: str = Field(..., description="The unique ID of the generated message.")
        timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the message.")
        is_user: bool = Field(False, description="True if the message is from the user, False if from the agent.")
        source_documents: Optional[List[SourceDocument]] = Field(None, description="List of source documents used for RAG.")
    ```

## 路径
`/backend/app/schemas/chat_schemas.py`