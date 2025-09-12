# `routers/rag.py` - RAG Routes

This document describes the `backend/app/routers/rag.py` file, which defines API routes related to RAG (Retrieval-Augmented Generation) functionality.

## Function Description
*   **RAG File List**: Provides an interface for retrieving a list of processed files in the RAG system, including their download URLs.
*   **RAG File Upload**: May provide a dedicated interface for uploading RAG knowledge base files.
*   **RAG File Deletion**: May provide an interface for deleting files from the RAG knowledge base.

## Logic Implementation
1.  **`list_rag_files(db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_active_user))`**:
    *   Retrieves user-uploaded `FileGist` records from the database.
    *   Generates MinIO presigned download URLs for each file (via `rag_file_service.get_file_gists_with_download_urls`).
    *   Returns a list of files including filename, upload time, download URL, and other information.
    *   `@router.get("/files")`

## Path
`/backend/app/routers/rag.py`