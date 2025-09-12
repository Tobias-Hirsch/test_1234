from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io
import logging
from typing import List
from minio import Minio

from app.models.database import get_db, FileGist, User
from app.services import auth, rag_file_service
from app.services import file_upload_service # Import the new service
from app.dependencies.permissions import check_permission # Import permission checker
from app.core.config import settings
from app.schemas import schemas
from app.services.query_filter_service import get_query_filter_service, QueryFilterService
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/{rag_id}/upload", response_model=List[schemas.FileGist])
async def upload_files_for_rag(
    rag_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """
    Uploads one or more files, stores them in MinIO, creates FileGist entries,
    and associates them with a RAG entry.
    This is the first step before triggering the embedding process.
    """
    # Check if user has permission to add files to this RAG item
    check_permission(db, current_user, "manage", resource_type="rag_data", resource_id=rag_id)

    try:
        created_gists = await file_upload_service.handle_file_uploads(db, rag_id, files)
        return created_gists
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to upload files for RAG ID {rag_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during file upload: {e}")

@router.get("/", response_model=List[schemas.FileGist])
def read_files(
    db: Session = Depends(get_db),
    qfs: QueryFilterService = Depends(get_query_filter_service),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieves a list of files, dynamically filtered based on the user's permissions.
    """
    filters = qfs.get_query_filters(resource_type="file", action="read_list")
    
    query = db.query(FileGist).filter(*filters)
    files = query.offset(skip).limit(limit).all()
    
    return files

@router.get("/{file_id}/content", response_class=StreamingResponse)
async def get_file_content(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """
    Acts as a secure proxy to stream file content from MinIO.
    """
    # First, retrieve the file gist to get the object name
    file_gist = db.query(FileGist).filter(FileGist.id == file_id).first()
    if not file_gist:
        raise HTTPException(status_code=404, detail="File not found.")

    # TODO: Add permission check here if necessary, to ensure the current_user
    # has access to the RAG item associated with this file.

    try:
        minio_client = None
        minio_bucket_name = None

        if file_gist.is_third_party:
            endpoint = settings.CUSTOMER_MINIO_ENDPOINT
            access_key = settings.CUSTOMER_MINIO_ACCESS_KEY
            secret_key = settings.CUSTOMER_MINIO_SECRET_KEY
            minio_bucket_name = settings.CUSTOMER_MINIO_BUCKET_NAME
            if not all([endpoint, access_key, secret_key, minio_bucket_name]):
                raise ValueError("CUSTOMER MinIO settings are not fully configured.")
            secure = "https" in endpoint
            clean_endpoint = endpoint.replace("https://", "").replace("http://", "")
            minio_client = file_upload_service.Minio(clean_endpoint, access_key=access_key, secret_key=secret_key, secure=secure)
        else:
            endpoint = settings.MINIO_ENDPOINT
            access_key = settings.MINIO_ACCESS_KEY
            secret_key = settings.MINIO_SECRET_KEY
            minio_bucket_name = settings.MINIO_BUCKET_NAME
            if not all([endpoint, access_key, secret_key, minio_bucket_name]):
                raise ValueError("Default MinIO settings are not fully configured.")
            secure = "https" in endpoint
            clean_endpoint = endpoint.replace("https://", "").replace("http://", "")
            minio_client = file_upload_service.Minio(clean_endpoint, access_key=access_key, secret_key=secret_key, secure=secure)

        # Get the file object from MinIO
        file_object = minio_client.get_object(minio_bucket_name, file_gist.filename)

        # Stream the file content back to the client
        return StreamingResponse(file_object.stream(32*1024), media_type='application/octet-stream')

    except Exception as e:
        print(f"Error streaming file from MinIO: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve file content.")
