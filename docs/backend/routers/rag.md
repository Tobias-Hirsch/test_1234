# `routers/rag.py` - RAG 路由

本文档描述了 `backend/app/routers/rag.py` 文件，该文件定义了与 RAG（Retrieval-Augmented Generation）功能相关的 API 路由。

## 功能描述
*   **RAG 文件列表**: 提供获取 RAG 系统中已处理文件列表的接口，包括其下载 URL。
*   **RAG 文件上传**: 可能提供专门用于 RAG 知识库文件上传的接口。
*   **RAG 文件删除**: 可能提供删除 RAG 知识库中文件的接口。

## 逻辑实现
1.  **`list_rag_files(db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_active_user))`**:
    *   从数据库中检索用户上传的 `FileGist` 记录。
    *   为每个文件生成 MinIO 预签名下载 URL（通过 `rag_file_service.get_file_gists_with_download_urls`）。
    *   返回包含文件名、上传时间、下载 URL 等信息的文件列表。
    *   `@router.get("/files")`

## 路径
`/backend/app/routers/rag.py`