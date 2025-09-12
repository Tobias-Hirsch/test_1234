# `services/conversation_cleaner.py` - Conversation Cleaner Service

This document describes the `backend/app/services/conversation_cleaner.py` file, which contains the business logic for periodically cleaning up old chat conversations.

## Function Description
*   **Periodic Cleanup**: Automatically deletes chat conversations that exceed a specified retention period.
*   **Data Maintenance**: Helps manage database size, improve query efficiency, and comply with data retention policies.

## Logic Implementation
1.  **`remove_old_conversations()`**:
    *   Retrieves the `CONVERSATION_CLEANUP_DAYS` configuration from `backend.app.core.config` to determine the conversation retention period.
    *   Calculates the cutoff date for conversations that need to be deleted.
    *   Connects to the MongoDB database.
    *   Finds and deletes all conversations in the `conversations` collection whose creation time is earlier than the cutoff date.
    *   Logs the cleanup operation.

## Path
`/backend/app/services/conversation_cleaner.py`