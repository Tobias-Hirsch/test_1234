# `services/chat_data_service.py` - Chat Data Service

This document describes the `backend/app/services/chat_data_service.py` file, which contains the business logic related to storing and retrieving chat messages and conversation data.

## Function Description
*   **Message Storage**: Saves chat messages (user and agent) to the database.
*   **Conversation Management**: Creates and manages chat conversations.
*   **History Retrieval**: Retrieves chat history for a specific conversation.
*   **Data Structuring**: Ensures chat data is stored in a consistent structure.

## Logic Implementation
This module primarily interacts with the MongoDB database to store chat messages and conversation metadata.

1.  **`save_message(conversation_id: str, message_content: str, is_user: bool, source_documents: Optional[List[dict]] = None)`**:
    *   Saves a single chat message to the `messages` collection in MongoDB.
    *   Messages include `conversation_id`, `content`, `is_user`, `timestamp`, and optional `source_documents`.
2.  **`get_conversation_messages(conversation_id: str) -> List[dict]`**:
    *   Retrieves all messages from the `messages` collection based on `conversation_id`.
    *   Sorts and returns by timestamp.
3.  **`create_conversation(user_id: int) -> str`**:
    *   Creates a new conversation record in the `conversations` collection in MongoDB.
    *   Returns the newly generated `conversation_id`.

## Path
`/backend/app/services/chat_data_service.py`