# `rag_knowledge/generic_knowledge.py` - Generic RAG Knowledge Processing

This document describes the `backend/app/rag_knowledge/generic_knowledge.py` file, which contains the generic logic for processing RAG (Retrieval-Augmented Generation) knowledge, including document processing, Milvus search, and interaction with LLMs.

## Function Description
*   **Document Processing**: Processes raw documents (e.g., Markdown files) into text chunks usable for RAG.
*   **Milvus Search**: Performs similarity search in the Milvus vector database based on user queries to retrieve relevant document chunks.
*   **LLM Interaction**: Provides retrieved document chunks as context to a Large Language Model (LLM) to generate augmented responses.
*   **File Metadata Processing**: Extracts and manages document metadata, such as filename, download URL, and summary.

## Logic Implementation
1.  **`process_markdown_file(file_path: str, filename: str, user_id: int, db: Session)`**:
    *   Reads Markdown file content.
    *   Splits file content into multiple text chunks.
    *   Generates embeddings for each text chunk (using `embedding_service`).
    *   Stores text chunks, embeddings, filename, file path, summary, and other information into Milvus and MongoDB.
    *   Updates `FileGist` database records.
2.  **`search_in_milvus(query: str, top_k: int = 5)`**:
    *   Generates embeddings for the user query.
    *   Performs vector similarity search in Milvus to retrieve the `top_k` most relevant document chunks to the query.
    *   Returns a list of `Document` objects containing document content, metadata (e.g., filename, download URL, summary).
3.  **`query_rag_system(query: str, db_session: Session)`**:
    *   This is the core function of the RAG system.
    *   First calls `search_in_milvus` to retrieve relevant documents.
    *   Then, retrieves summaries and original chunk content of these documents from MongoDB (via `rag_file_service`).
    *   Constructs a context containing the retrieved information (filename, download URL, summary, relevant chunks).
    *   Passes this context along with the user query to the LLM (via functions in `backend.app.llm.chain`), guiding the LLM to use this information to generate a response, including clickable download links in Markdown format.

## Path
`/backend/app/rag_knowledge/generic_knowledge.py`