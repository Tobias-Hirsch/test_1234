# backend/app/routers/knowledge_base.py
import os
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db, RagData, FileGist, User
from app.services import auth
from app.dependencies.permissions import check_permission
from app.rag_knowledge.generic_knowledge import get_mongo_client, delete_milvus_data_by_filepath, delete_mongo_data_by_filename
from app.modules.minio_module import delete_document_from_minio
from app.schemas import schemas # Assuming schemas for FileGist exist

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/{rag_id}/documents", response_model=List[schemas.FileGist])
async def list_rag_documents(
    rag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """
    Lists all documents (FileGists) associated with a specific RAG entry,
    including their processing status from MongoDB.
    """
    check_permission(db, current_user, "read", resource_type="rag_data", resource_id=rag_id)

    rag_entry = db.query(RagData).filter(RagData.id == rag_id).first()
    if not rag_entry:
        raise HTTPException(status_code=404, detail="RAG entry not found")

    file_gists = db.query(FileGist).filter(FileGist.rag_id == rag_id).all()
    
    # Here you could augment the file_gists with status from MongoDB if needed
    # For now, we return the basic FileGist schema

    return file_gists

@router.delete("/{rag_id}/documents/{file_gist_id}")
async def delete_rag_document(
    rag_id: int,
    file_gist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """
    Deletes a document and its associated data from MinIO, Milvus, MongoDB,
    and the SQL database.
    """
    check_permission(db, current_user, "manage", resource_type="rag_data", resource_id=rag_id)

    rag_entry = db.query(RagData).filter(RagData.id == rag_id).first()
    if not rag_entry:
        raise HTTPException(status_code=404, detail="RAG entry not found")

    file_gist = db.query(FileGist).filter(FileGist.id == file_gist_id, FileGist.rag_id == rag_id).first()
    if not file_gist:
        raise HTTPException(status_code=404, detail="File not found in this RAG entry")

    try:
        # Construct dynamic names
        dynamic_name = rag_entry.name.lower().replace(" ", "_")
        milvus_collection_name = f"rag_{dynamic_name}"
        mongo_db_name = f"rag_db_{dynamic_name}"
        mongo_collection_name = f"documents_{dynamic_name}"
        
        object_name = file_gist.filename # This is the full path-like name in MinIO
        original_filename_base = os.path.basename(object_name)

        # 1. Delete from Milvus
        logger.info(f"Deleting from Milvus: collection='{milvus_collection_name}', filepath='{object_name}'")
        await delete_milvus_data_by_filepath(milvus_collection_name, object_name)

        # 2. Delete from MongoDB
        logger.info(f"Deleting from MongoDB: db='{mongo_db_name}', collection='{mongo_collection_name}', filename='{original_filename_base}'")
        await delete_mongo_data_by_filename(mongo_db_name, mongo_collection_name, original_filename_base)

        # 3. Delete from MinIO
        logger.info(f"Deleting from MinIO: bucket='{rag_entry.minio_bucket_name}', object='{object_name}'")
        delete_document_from_minio(object_name, rag_entry.minio_bucket_name)

        # 4. Delete from SQL database
        logger.info(f"Deleting from PostgreSQL: file_gist_id='{file_gist_id}'")
        db.delete(file_gist)
        db.commit()

        return {"message": f"Successfully deleted '{original_filename_base}' and all its associated data."}

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete document {file_gist.filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred during deletion: {e}")
