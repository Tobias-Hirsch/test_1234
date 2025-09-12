# `schemas/schemas.py` - General Data Schemas

This document describes the `backend/app/schemas/schemas.py` file, which defines various Pydantic data schemas used in the application for request body validation, response serialization, and data model definition.

## Function Description
*   **Request Body Validation**: Defines the structure and types of input data received by API interfaces.
*   **Response Serialization**: Defines the structure and types of output data returned by API interfaces.
*   **Data Models**: Serves as a data conversion layer between database models (SQLAlchemy ORM models) and the API.
*   **Data Validation**: Leverages Pydantic's powerful features for data type checking and validation.

## Logic Implementation
This file typically contains classes inheriting from `pydantic.BaseModel`, with each class defining a specific data structure.

For example, it might include the following schemas:
*   **`UserBase`**: Basic user information (e.g., `username`, `email`).
*   **`UserCreate`**: Request body for user creation, potentially including a password.
*   **`UserUpdate`**: Request body for user updates.
*   **`UserInDB`**: Full user information in the database, potentially including a hashed password.
*   **`Token`**: Response schema for JWT tokens (`access_token`, `token_type`).
*   **`TokenData`**: Data schema contained within JWT tokens (`username`).
*   **`Message`**: General message response schema (`message`).
*   **`FileGistBase`**: Basic file information.
*   **`FileGistCreate`**: Request body for file creation.
*   **`FileGistResponse`**: File list response schema, potentially including `download_url`.
*   **`AgentChatRequest`**: Agent chat request schema, including user message and conversation ID.
*   **`AgentChatResponse`**: Agent chat response schema, including agent reply.

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

## Path
`/backend/app/schemas/schemas.py`