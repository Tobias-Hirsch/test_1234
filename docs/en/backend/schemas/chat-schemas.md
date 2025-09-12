# `schemas/chat_schemas.py` - Chat Data Schemas

This document describes the `backend/app/schemas/chat_schemas.py` file, which specifically defines data schemas for chat functionality.

## Function Description
*   **Chat Request**: Defines the request body structure for users sending chat messages.
*   **Chat Response**: Defines the response body structure returned by the chat system, including message content, conversation ID, message ID, timestamp, etc.
*   **RAG Source Document**: Defines the structure of source documents retrieved in RAG functionality, including filename, download URL, and summary.

## Logic Implementation
This file typically contains classes inheriting from `pydantic.BaseModel`, used to define chat-related input and output data structures.

For example, it might include the following schemas:
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

## Path
`/backend/app/schemas/chat_schemas.py`