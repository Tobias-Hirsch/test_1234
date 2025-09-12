# `schemas/schemas.py` - 通用数据模式

本文档描述了 `backend/app/schemas/schemas.py` 文件，该文件定义了应用程序中使用的各种 Pydantic 数据模式（Schema），用于请求体验证、响应序列化和数据模型定义。

## 功能描述
*   **请求体验证**: 定义 API 接口接收的输入数据的结构和类型。
*   **响应序列化**: 定义 API 接口返回的输出数据的结构和类型。
*   **数据模型**: 作为数据库模型（SQLAlchemy ORM 模型）和 API 之间的数据转换层。
*   **数据验证**: 利用 Pydantic 的强大功能进行数据类型检查和验证。

## 逻辑实现
该文件通常包含继承自 `pydantic.BaseModel` 的类，每个类定义一个特定的数据结构。

例如，可能包含以下模式：
*   **`UserBase`**: 用户基本信息（如 `username`, `email`）。
*   **`UserCreate`**: 用户创建时的请求体，可能包含密码。
*   **`UserUpdate`**: 用户更新时的请求体。
*   **`UserInDB`**: 数据库中用户的完整信息，可能包含哈希密码。
*   **`Token`**: JWT 令牌的响应模式（`access_token`, `token_type`）。
*   **`TokenData`**: JWT 令牌中包含的数据模式（`username`）。
*   **`Message`**: 通用消息响应模式（`message`）。
*   **`FileGistBase`**: 文件基本信息。
*   **`FileGistCreate`**: 文件创建时的请求体。
*   **`FileGistResponse`**: 文件列表响应模式，可能包含 `download_url`。
*   **`AgentChatRequest`**: 代理聊天请求模式，包含用户消息和会话 ID。
*   **`AgentChatResponse`**: 代理聊天响应模式，包含代理回复。

```python
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class UserInDBBase(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # or orm_mode = True for Pydantic v1

class User(UserInDBBase):
    pass

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

# Message Schema
class Message(BaseModel):
    message: str

# FileGist Schemas
class FileGistBase(BaseModel):
    filename: str
    file_path: str

class FileGistCreate(FileGistBase):
    pass

class FileGistResponse(FileGistBase):
    id: int
    upload_time: datetime
    user_id: int
    download_url: Optional[str] = None # Added for RAG links

    class Config:
        from_attributes = True

# Chat Schemas (from chat_schemas.py, but often combined or referenced)
class AgentChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class AgentChatResponse(BaseModel):
    response: str
    conversation_id: str
    message_id: str
    timestamp: datetime
    is_user: bool
    source_documents: Optional[List[dict]] = None # For RAG sources
```

## 路径
`/backend/app/schemas/schemas.py`