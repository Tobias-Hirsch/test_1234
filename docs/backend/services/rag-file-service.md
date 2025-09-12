# `services/rag_file_service.py` - RAG 文件服务

本文档描述了 `backend/app/services/rag_file_service.py` 文件，该文件集中了与 RAG（Retrieval-Augmented Generation）相关的文件处理和数据检索逻辑。

## 功能描述
*   **文件元数据检索**: 从数据库中获取 `FileGist` 对象的详细信息。
*   **MinIO 预签名 URL 生成**: 为 `FileGist` 对象生成 MinIO 预签名下载 URL。
*   **MongoDB 摘要和块检索**: 从 MongoDB 中检索与文件相关的摘要和原始文本块。
*   **统一数据接口**: 提供一个统一的接口来获取 RAG 所需的所有文件相关数据。

## 逻辑实现
1.  **`get_file_gists_with_download_urls(db: Session, file_gists: List[FileGist]) -> List[schemas.FileGistResponse]`**:
    *   接收一个 `FileGist` 对象列表。
    *   遍历每个 `FileGist`，调用 `minio_module.get_presigned_download_url` 为其生成下载 URL。
    *   将 `FileGist` 对象转换为 `schemas.FileGistResponse` 模式，并包含 `download_url`。
    *   返回包含下载 URL 的文件列表。
2.  **`get_rag_document_data(file_path: str) -> Optional[dict]`**:
    *   根据文件路径从 MongoDB 的 `rag_documents` 集合中检索文档数据。
    *   返回包含 `summary` 和 `chunks` 等信息的字典。

## 路径
`/backend/app/services/rag_file_service.py`