# `routers/files.py` - 文件管理路由

本文档描述了 `backend/app/routers/files.py` 文件，该文件定义了与文件上传、下载和管理相关的 API 路由。

## 功能描述
*   **文件上传**: 提供用户上传文件的接口。
*   **文件下载**: 提供用户下载文件的接口。
*   **文件列表**: 提供获取用户已上传文件列表的接口。
*   **文件删除**: 提供删除已上传文件的接口。

## 逻辑实现
1.  **`upload_file(file: UploadFile = File(...), current_user: User = Depends(auth.get_current_active_user), db: Session = Depends(get_db))`**:
    *   接收上传的文件。
    *   将文件保存到 MinIO 存储。
    *   在数据库中记录文件元数据（如文件名、路径、用户 ID）。
    *   可能触发后续的文件处理流程（如 PDF 转 Markdown，然后进行 RAG 嵌入）。
    *   `@router.post("/uploadfile")`
2.  **`download_file(file_id: int, current_user: User = Depends(auth.get_current_active_user), db: Session = Depends(get_db))`**:
    *   根据 `file_id` 从数据库中查找文件信息。
    *   从 MinIO 获取文件的预签名下载 URL，或直接读取文件内容并作为流返回。
    *   `@router.get("/download/{file_id}")`
3.  **`list_files(current_user: User = Depends(auth.get_current_active_user), db: Session = Depends(get_db))`**:
    *   获取当前用户已上传的文件列表。
    *   返回文件元数据，包括文件名和下载 URL。
    *   `@router.get("/list_files")`
4.  **`delete_file(file_id: int, current_user: User = Depends(auth.get_current_active_user), db: Session = Depends(get_db))`**:
    *   根据 `file_id` 删除 MinIO 中的文件和数据库中的文件记录。
    *   `@router.delete("/delete_file/{file_id}")`

## 路径
`/backend/app/routers/files.py`