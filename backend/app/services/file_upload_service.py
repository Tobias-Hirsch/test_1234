# backend/app/services/file_upload_service.py
import logging
import uuid
from typing import List
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.database import FileGist, RagData
from app.modules.minio_module import Minio, S3Error, settings

logger = logging.getLogger(__name__)

def get_minio_client():
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=False
    )

async def handle_file_uploads(db: Session, rag_id: int, files: List[UploadFile]) -> List[FileGist]:
    """
    Handles uploading multiple files to MinIO and creating FileGist records.

    Args:
        db: The database session.
        rag_id: The ID of the RAG entry to associate the files with.
        files: A list of files to upload.

    Returns:
        A list of the created FileGist objects.
    """
    rag_entry = db.query(RagData).filter(RagData.id == rag_id).first()
    if not rag_entry:
        raise ValueError("RAG entry not found")

    minio_client = get_minio_client()
    bucket_name = rag_entry.minio_bucket_name
    created_gists = []

    try:
        # Ensure bucket exists
        found = minio_client.bucket_exists(bucket_name)
        if not found:
            minio_client.make_bucket(bucket_name)
            logger.info(f"Bucket '{bucket_name}' created.")

        for file in files:
            # Sanitize filename
            original_filename = file.filename
            # Create a unique object name to prevent overwrites
            object_name = f"{rag_id}/{uuid.uuid4()}_{original_filename}"
            
            file_content = await file.read()
            file_size = len(file_content)

            # Reset file pointer after reading
            await file.seek(0)

            # Upload to MinIO
            minio_client.put_object(
                bucket_name,
                object_name,
                file,
                length=file_size,
                content_type=file.content_type
            )
            logger.info(f"Successfully uploaded '{original_filename}' to '{object_name}' in bucket '{bucket_name}'.")

            # Create FileGist record
            new_gist = FileGist(
                filename=object_name, # Store the full object name
                rag_id=rag_id,
                user_id=rag_entry.user_id, # Associate with the RAG owner
                file_size=file_size,
                content_type=file.content_type,
                original_filename=original_filename # Store the original filename for display
            )
            db.add(new_gist)
            db.commit()
            db.refresh(new_gist)
            created_gists.append(new_gist)

    except S3Error as e:
        logger.error(f"MinIO error during file upload for RAG ID {rag_id}: {e}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during file upload: {e}")
        db.rollback()
        raise

    return created_gists