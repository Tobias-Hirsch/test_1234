# `services/rag_file_service.py` - RAG File Service

This document describes the `backend/app/services/rag_file_service.py` file, which centralizes file processing and data retrieval logic related to RAG (Retrieval-Augmented Generation).

## Function Description
*   **File Metadata Retrieval**: Retrieves detailed information about `FileGist` objects from the database.
*   **MinIO Presigned URL Generation**: Generates MinIO presigned download URLs for `FileGist` objects.
*   **MongoDB Summary and Chunk Retrieval**: Retrieves file-related summaries and raw text chunks from MongoDB.
*   **Unified Data Interface**: Provides a unified interface to obtain all file-related data required for RAG.

## Logic Implementation
1.  **`get_file_gists_with_download_urls(db: Session, file_gists: List[FileGist]) -> List[schemas.FileGistResponse]`**:
    *   Receives a list of `FileGist` objects.
    *   Iterates through each `FileGist` and calls `minio_module.get_presigned_download_url` to generate a download URL for it.
    *   Converts the `FileGist` object to the `schemas.FileGistResponse` schema, including the `download_url`.
    *   Returns a list of files containing download URLs.
2.  **`get_rag_document_data(file_path: str) -> Optional[dict]`**:
    *   Retrieves document data from the `rag_documents` collection in MongoDB based on the file path.
    *   Returns a dictionary containing information such as `summary` and `chunks`.

## Path
`/backend/app/services/rag_file_service.py`