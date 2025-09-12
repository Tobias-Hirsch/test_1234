# `modules/minio_module.py` - MinIO 对象存储模块

本文档描述了 `backend/app/modules/minio_module.py` 文件，该文件封装了与 MinIO 对象存储服务交互的功能。

## 功能描述
*   **客户端初始化**: 提供 MinIO 客户端的初始化和连接功能。
*   **文件上传**: 支持将文件上传到 MinIO 存储桶。
*   **文件下载**: 支持从 MinIO 存储桶下载文件。
*   **文件删除**: 支持从 MinIO 存储桶删除文件。
*   **预签名 URL 生成**: 生成 MinIO 对象的预签名 URL，用于临时授权访问。
*   **存储桶管理**: 提供创建和检查存储桶的功能。

## 逻辑实现
1.  **MinIO 客户端**: 使用 `minio` 库的 `Minio` 类来创建客户端实例，配置包括 MinIO 服务的端点、访问密钥和秘密密钥。
    ```python
    from minio import Minio
    from minio.error import S3Error
    from backend.app.core.config import settings
    import os

    minio_client: Minio = None

    async def connect_to_minio():
        global minio_client
        try:
            minio_client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=False # 根据您的MinIO部署配置为True或False
            )
            # 检查并创建桶
            found = minio_client.bucket_exists(settings.MINIO_BUCKET_NAME)
            if not found:
                minio_client.make_bucket(settings.MINIO_BUCKET_NAME)
                print(f"Bucket '{settings.MINIO_BUCKET_NAME}' created successfully.")
            else:
                print(f"Bucket '{settings.MINIO_BUCKET_NAME}' already exists.")
        except S3Error as e:
            print(f"Error connecting to MinIO: {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred during MinIO connection: {e}")
            raise
    ```
2.  **文件操作**: 提供异步函数来执行文件上传、下载和删除操作。
    *   **`upload_file_to_minio(file_path: str, file_content: bytes)`**: 将字节内容上传到指定路径。
    *   **`download_file_from_minio(file_path: str)`**: 从指定路径下载文件内容。
    *   **`delete_file_from_minio(file_path: str)`**: 删除指定路径的文件。
3.  **预签名 URL**: `presigned_get_object` 方法用于生成一个临时有效的 URL，允许用户在不经过后端认证的情况下直接从 MinIO 下载文件。
    ```python
    def get_presigned_download_url(object_name: str, expires_in_seconds: int = 3600) -> str:
        if not minio_client:
            raise Exception("MinIO client not initialized.")
        try:
            url = minio_client.presigned_get_object(
                settings.MINIO_BUCKET_NAME,
                object_name,
                expires=timedelta(seconds=expires_in_seconds)
            )
            return url
        except S3Error as e:
            print(f"Error generating presigned URL: {e}")
            raise
    ```

## 路径
`/backend/app/modules/minio_module.py`