# `modules/minio_module.py` - MinIO Object Storage Module

This document describes the `backend/app/modules/minio_module.py` file, which encapsulates functionalities for interacting with the MinIO object storage service.

## Function Description
*   **Client Initialization**: Provides functions for initializing and connecting the MinIO client.
*   **File Upload**: Supports uploading files to MinIO buckets.
*   **File Download**: Supports downloading files from MinIO buckets.
*   **File Deletion**: Supports deleting files from MinIO buckets.
*   **Presigned URL Generation**: Generates presigned URLs for MinIO objects, used for temporary authorized access.
*   **Bucket Management**: Provides functions for creating and checking buckets.

## Logic Implementation
1.  **MinIO Client**: Uses the `Minio` class from the `minio` library to create a client instance, with configuration including the MinIO service endpoint, access key, and secret key.
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
                secure=False # Set to True or False based on your MinIO deployment configuration
            )
            # Check and create bucket
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
2.  **File Operations**: Provides asynchronous functions to perform file upload, download, and deletion operations.
    *   **`upload_file_to_minio(file_path: str, file_content: bytes)`**: Uploads byte content to the specified path.
    *   **`download_file_from_minio(file_path: str)`**: Downloads file content from the specified path.
    *   **`delete_file_from_minio(file_path: str)`**: Deletes the file at the specified path.
3.  **Presigned URL**: The `presigned_get_object` method is used to generate a temporarily valid URL, allowing users to directly download files from MinIO without backend authentication.
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

## Path
`/backend/app/modules/minio_module.py`