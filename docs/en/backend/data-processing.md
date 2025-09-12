# Data Processing

This section describes the data processing flow of the Rosti backend, including RAG (Retrieval-Augmented Generation) process, attachment handling, and data storage.

## 1. RAG Data Processing Flow

*   **Document Upload and Parsing**: After users upload documents, the backend parses the document content (PDF, Word, Excel, etc.).
*   **Text Chunking and Embedding**: The parsed text is split into small chunks, and vector embeddings are generated using an embedding model.
*   **Vector Storage**: Vector embeddings are stored in the Milvus vector database for efficient similarity search.
*   **Summary Generation and Storage**: Summary information of document chunks is stored in MongoDB for quick overview in RAG responses.
*   **Permission Management**: Access permissions for RAG data are associated with user roles to ensure data security.

## 2. Chat Attachment Handling

*   **Upload and Storage**: Chat attachments uploaded by users are directly stored in MinIO object storage.
*   **Content Extraction**: For supported attachment types (e.g., PDF, Word, Excel), the backend attempts to extract their text content and pass it as context to the LLM.
*   **Download and Management**: Provides interfaces for downloading and deleting attachments.

## 3. Data Storage

*   **Relational Database (PostgreSQL/MySQL)**: Stores structured metadata such as users, conversations, and RAG items.
*   **MongoDB**: Stores chat messages, attachment metadata, and summary information of RAG documents.
*   **MinIO**: Object storage, used for storing original document files and chat attachments.
*   **Milvus**: Vector database, used for storing vector embeddings of document chunks.

## 4. LLM Interaction

*   **Context Building**: The backend constructs the LLM's input context based on user queries, chat history, RAG search results, and attachment content.
*   **Streaming Response**: LLM responses are streamed back to the frontend, providing a better user experience.
*   **Prompt Engineering**: Uses carefully designed prompts to guide the LLM in generating high-quality, cited answers.