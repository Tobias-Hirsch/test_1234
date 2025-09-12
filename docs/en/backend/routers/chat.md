# `routers/chat.py` - Chat Routes

This document describes the `backend/app/routers/chat.py` file, which defines API routes related to chat functionality.

## Function Description
*   **Send Chat Message**: Provides an interface for users to send messages to the chat system.
*   **Get Chat History**: Provides an interface for retrieving chat history for a specific conversation.
*   **Create New Conversation**: Provides an interface for creating new chat conversations.
*   **RAG Integration**: Integrates RAG (Retrieval-Augmented Generation) functionality into chat message processing, retrieving information from the knowledge base based on user queries and augmenting LLM responses.
*   **LLM Interaction**: Interacts with Large Language Models (LLMs) to generate chat replies.

## Logic Implementation
1.  **`add_conversation_message(message: schemas.AgentChatRequest, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_active_user))`**:
    *   Receives chat messages sent by the user.
    *   If RAG is enabled (direct chat path when `AGENTIC_RAG_ENABLE=False`), calls `rag_knowledge.generic_knowledge.query_rag_system` to retrieve relevant documents and summaries.
    *   Constructs the LLM's system prompt, passing retrieved RAG information (including filename, download URL, summary) as context to the LLM.
    *   Calls the LLM (via functions in `backend.app.llm.chain`) to generate a reply.
    *   Saves user messages and LLM replies to the database (MongoDB).
    *   Returns the LLM-generated reply.
    *   `@router.post("/add_conversation_message")`
2.  **`get_conversation_history(conversation_id: str, current_user: User = Depends(auth.get_current_active_user))`**:
    *   Retrieves chat history from MongoDB based on `conversation_id`.
    *   Returns a list of chat messages.
    *   `@router.get("/history/{conversation_id}")`
3.  **`create_new_conversation(current_user: User = Depends(auth.get_current_active_user))`**:
    *   Creates a new chat conversation for the current user.
    *   Returns the ID of the new conversation.
    *   `@router.post("/new_conversation")`

## Path
`/backend/app/routers/chat.py`