# API Endpoints

This section lists the main RESTful API endpoints provided by the Rosti backend and their functionalities.

## 1. Authentication and User Management

*   **`/auth/login`**: User login, obtain authentication token.
*   **`/auth/register`**: New user registration.
*   **`/users/me`**: Get current user information.

## 2. Chat Functionality

*   **`/chat/conversations`**: Get user conversation list, create new conversation.
*   **`/chat/conversations/{conversation_id}/messages`**: Get conversation messages, add new messages.
*   **`/chat/upload_files`**: Upload chat attachments.
*   **`/chat/conversations/{conversation_id}/messages/{message_id}/attachments/{attachment_id}/download`**: Download chat attachments.

## 3. Knowledge Base (RAG) Management

*   **`/rag/items`**: Get knowledge base item list, create new item.
*   **`/rag/items/{rag_id}/files`**: Get file list under knowledge base item, upload new files.
*   **`/rag/items/{rag_id}/files/{file_id}/download`**: Download knowledge base files.

## 4. Tools and Services

*   **`/tools/search`**: Online search tool API.
*   **`/tools/pdf-process`**: PDF processing tool API.

## 5. Data Models

*   **`User`**: User data model.
*   **`Conversation`**: Conversation data model.
*   **`Message`**: Message data model, includes attachment information.
*   **`Attachment`**: Attachment data model, includes MinIO storage information.
*   **`RagItem`**: Knowledge base item data model.
*   **`FileGist`**: Knowledge base file metadata model.

Each API supports JSON requests and responses, and adheres to RESTful design principles.