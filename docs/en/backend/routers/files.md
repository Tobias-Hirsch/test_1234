# `routers/files.py` - File Management Routes

This document describes the `backend/app/routers/files.py` file, which defines API routes related to file upload, download, and management.

## Function Description
*   **File Upload**: Provides an interface for users to upload files.
*   **File Download**: Provides an interface for users to download files.
*   **File Listing**: Provides an interface for retrieving a list of files uploaded by the user.
*   **File Deletion**: Provides an interface for deleting uploaded files.

## Logic Implementation
1.  **`upload_file(file: UploadFile = File(...), current_user: User = Depends(auth.get_current_active_user), db: Session = Depends(get_db))`**:
    *   Receives the uploaded file.
    *   Saves the file to MinIO storage.
    *   Records file metadata (e.g., filename, path, user ID) in the database.
    *   May trigger subsequent file processing workflows (e.g., PDF to Markdown conversion, then RAG embedding).
    *   `@router.post("/uploadfile")`
2.  **`download_file(file_id: int, current_user: User = Depends(auth.get_current_active_user), db: Session = Depends(get_db))`**:
    *   Retrieves file information from the database based on `file_id`.
    *   Obtains a presigned download URL for the file from MinIO, or directly reads the file content and returns it as a stream.
    *   `@router.get("/download/{file_id}")`
3.  **`list_files(current_user: User = Depends(auth.get_current_active_user), db: Session = Depends(get_db))`**:
    *   Retrieves a list of files uploaded by the current user.
    *   Returns file metadata, including filename and download URL.
    *   `@router.get("/list_files")`
4.  **`delete_file(file_id: int, current_user: User = Depends(auth.get_current_active_user), db: Session = Depends(get_db))`**:
    *   Deletes the file in MinIO and the file record in the database based on `file_id`.
    *   `@router.delete("/delete_file/{file_id}")`

## Path
`/backend/app/routers/files.py`