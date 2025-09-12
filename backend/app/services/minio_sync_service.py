# Developer: Jinglu Han
# mailbox: admin@de-manufacturing.cn

import logging
from minio import Minio
from ..core.config import settings
import asyncio
from app.models.database import get_db
from app.services import rag_file_service
from app.rag_knowledge.generic_knowledge import process_and_embed_pdf # Assuming PDF for now
from sqlalchemy.orm import Session
import os

# Configure logger
logger = logging.getLogger(__name__)

# --- Customer MinIO Client ---
_customer_minio_client = None

def get_customer_minio_client():
    """Initializes and returns a Minio client for the customer's instance."""
    global _customer_minio_client
    if _customer_minio_client is None:
        try:
            endpoint = settings.CUSTOMER_MINIO_ENDPOINT.replace("http://", "").replace("https://", "")
            _customer_minio_client = Minio(
                endpoint,
                access_key=settings.CUSTOMER_MINIO_ACCESS_KEY,
                secret_key=settings.CUSTOMER_MINIO_SECRET_KEY,
                secure=settings.CUSTOMER_MINIO_ENDPOINT.startswith("https://")
            )
            logger.info(f"Successfully initialized customer MinIO client for endpoint: {endpoint}")
        except Exception as e:
            logger.error(f"Failed to initialize customer MinIO client: {e}", exc_info=True)
            _customer_minio_client = "failed_to_initialize"
    
    return _customer_minio_client if _customer_minio_client != "failed_to_initialize" else None

async def list_files_from_customer_minio() -> dict:
    """
    Lists all files from the customer's MinIO bucket and groups them by their top-level subdirectory.
    Returns a dictionary where keys are subdirectory names and values are lists of file info.
    Files in the root of the bucket are ignored.
    """
    client = get_customer_minio_client()
    if not client:
        logger.error("Cannot list files, customer MinIO client is not available.")
        return {}

    try:
        bucket_name = settings.CUSTOMER_MINIO_BUCKET_NAME
        logger.info(f"Listing files and grouping by subdirectory from bucket: {bucket_name}")
        
        loop = asyncio.get_running_loop()
        objects = await loop.run_in_executor(
            None,
            lambda: list(client.list_objects(bucket_name, recursive=True))
        )
        
        grouped_files = {}
        # Heuristic list of extensions to identify file-like directory names
        FILE_LIKE_EXTENSIONS = {'.js', '.docx', '.pdf', '.xls', '.xlsx', '.doc', '.pub'}
        DEFAULT_RAG_NAME = "minio_root_files" # RAG name for ungrouped files

        for obj in objects:
            if obj.is_dir:
                continue
            
            object_name = obj.object_name
            parts = object_name.split('/', 1)
            
            group_name = DEFAULT_RAG_NAME
            
            # Check if there is a top-level directory
            if len(parts) > 1 and parts[0]:
                potential_group = parts[0]
                # Check if the directory name looks like a file
                _, ext = os.path.splitext(potential_group)
                if ext.lower() not in FILE_LIKE_EXTENSIONS:
                    group_name = potential_group # It's a real directory
            
            if group_name == DEFAULT_RAG_NAME:
                 logger.info(f"File '{object_name}' is being grouped into default RAG '{DEFAULT_RAG_NAME}'.")
            
            if group_name not in grouped_files:
                grouped_files[group_name] = []
            
            grouped_files[group_name].append({"path": object_name, "etag": obj.etag})

        # Log the final grouping
        group_count = len(grouped_files)
        default_group_size = len(grouped_files.get(DEFAULT_RAG_NAME, []))
        logger.info(f"Found {group_count} group(s) to process in customer bucket '{bucket_name}'.")
        if default_group_size > 0:
            logger.info(f"The default group '{DEFAULT_RAG_NAME}' contains {default_group_size} file(s).")
        return grouped_files
    except Exception as e:
        logger.error(f"An error occurred while listing files from customer MinIO: {e}", exc_info=True)
        return {}

async def process_single_file(file_info: dict, db: Session, rag_id: int, rag_name: str):
    """
    Downloads, processes, and embeds a single file with retry logic.
    """
    client = get_customer_minio_client()
    if not client:
        return

    file_path = file_info["path"]
    file_etag = file_info["etag"]
    max_retries = settings.MINIO_SYNC_MAX_RETRIES
    
    for attempt in range(max_retries):
        try:
            logger.info(f"[Attempt {attempt + 1}/{max_retries}] Processing file: {file_path}")
            
            # 1. Download file from customer MinIO
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.get_object(settings.CUSTOMER_MINIO_BUCKET_NAME, file_path)
            )
            file_bytes = response.read()
            response.close()
            response.release_conn()
            
            logger.info(f"Successfully downloaded {file_path} ({len(file_bytes)} bytes).")

            # 2. Determine file type and call appropriate processor
            # For now, we assume all are PDFs as per generic_knowledge structure.
            # This can be expanded with a file type dispatcher.
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == ".pdf":
                # This is where we call the existing embedding pipeline
                # We need to construct the dynamic collection/db names
                sanitized_rag_name = rag_name.lower().replace(" ", "_")
                milvus_collection_name = f"rag_{sanitized_rag_name}"
                mongo_db_name = f"rag_db_{sanitized_rag_name}"

                logger.info(f"Embedding '{file_path}' into Milvus collection '{milvus_collection_name}' and Mongo DB '{mongo_db_name}'")
                
                chunk_count = await process_and_embed_pdf(
                    file_bytes=file_bytes,
                    original_filename=file_path,
                    milvus_collection_name=milvus_collection_name,
                    mongo_db_name=mongo_db_name,
                    rag_id=rag_id
                )
                
                if chunk_count > 0:
                    logger.info(f"Successfully embedded {chunk_count} chunks for {file_path}.")
                    # 3. Create/Update file_gist record
                    rag_file_service.create_or_update_file_gist(
                        db=db,
                        rag_id=rag_id,
                        filename=file_path,
                        file_path_in_minio=file_path, # Storing the path in customer's minio
                        etag=file_etag,
                        is_third_party=True # Mark as a third-party file
                    )
                    logger.info(f"Successfully updated file_gist for {file_path}.")
                    return # Success, exit retry loop
                else:
                    raise ValueError("Embedding process returned 0 chunks, indicating a failure.")
            else:
                logger.warning(f"Skipping file with unsupported extension '{file_extension}': {file_path}")
                return # Not an error, just unsupported type

        except Exception as e:
            logger.error(f"Failed to process file {file_path} on attempt {attempt + 1}: {e}", exc_info=True)
            if attempt < max_retries - 1:
                logger.info(f"Retrying in 10 seconds...")
                await asyncio.sleep(10)
            else:
                logger.critical(f"All {max_retries} attempts failed for {file_path}. Giving up. Please check logs for details.")
                # Optionally update a status in the database to 'failed' for manual intervention
                rag_file_service.create_or_update_file_gist(
                    db=db,
                    rag_id=rag_id,
                    filename=file_path,
                    file_path_in_minio=file_path,
                    etag=f"FAILED:{file_etag}", # Mark as failed
                    is_third_party=True
                )


async def sync_minio_bucket():
    """
    Main synchronization logic. Detects subdirectories in the customer MinIO bucket,
    ensures a corresponding RAG item exists (creating it if necessary), and syncs
    new or modified files into that RAG item.
    """
    logger.info("Starting periodic MinIO bucket synchronization task...")
    db: Session = next(get_db())
    try:
        # 1. Get all files from MinIO, grouped by subdirectory
        grouped_remote_files = await list_files_from_customer_minio()
        if not grouped_remote_files:
            logger.info("No subdirectories with files found in remote MinIO bucket. Sync task finished.")
            return

        # 2. Iterate through each subdirectory found in MinIO
        for rag_name, remote_files in grouped_remote_files.items():
            logger.info(f"--- Processing subdirectory (RAG): '{rag_name}' with {len(remote_files)} files ---")

            # 2a. Find or create the corresponding RAG item in our database
            rag_item = rag_file_service.get_rag_item_by_name(db, rag_name)
            if not rag_item:
                logger.info(f"RAG item '{rag_name}' not found. Attempting to create it automatically.")
                rag_item = rag_file_service.create_rag_item(
                    db,
                    name=rag_name,
                    description=f"Auto-created for MinIO sync from subdirectory '{rag_name}'"
                )
                if not rag_item:
                    logger.error(f"Failed to create RAG item for '{rag_name}'. Skipping this subdirectory.")
                    continue # Move to the next subdirectory
            
            # 2b. Get the state of already processed files for this specific RAG item
            local_files_gist = rag_file_service.get_all_file_gists_for_rag_item(db, rag_id=rag_item.id, is_third_party=True)
            local_files_map = {f.filename: f.etag for f in local_files_gist}
            logger.info(f"Found {len(local_files_map)} tracked third-party files for '{rag_item.name}'.")

            # 2c. Determine which files are new or have been modified
            files_to_process = []
            for remote_file in remote_files:
                remote_path = remote_file["path"]
                remote_etag = remote_file["etag"]
                local_etag = local_files_map.get(remote_path)
                
                if not local_etag or local_etag != remote_etag:
                    if not local_etag:
                        logger.info(f"New file for '{rag_item.name}': {remote_path}")
                    else:
                        logger.info(f"Modified file for '{rag_item.name}': {remote_path} (Old ETag: {local_etag}, New ETag: {remote_etag})")
                    files_to_process.append(remote_file)

            # Apply file limit per subdirectory if configured
            try:
                # Get the limit from settings, default to 0 (no limit)
                limit = int(settings.MINIO_SYNC_FILES_PER_SUBDIR_LIMIT)
                if limit > 0 and len(files_to_process) > limit:
                    logger.info(f"Applying limit: {len(files_to_process)} files found, processing the first {limit} for RAG '{rag_name}'.")
                    files_to_process = files_to_process[:limit]
            except (AttributeError, ValueError, TypeError):
                # This will happen if the setting is not defined, is None, or not a valid integer.
                # We can safely ignore it and proceed without a limit.
                pass

            # 2d. Process the new/modified files
            if not files_to_process:
                logger.info(f"RAG item '{rag_item.name}' is up-to-date.")
            else:
                logger.info(f"Found {len(files_to_process)} new/modified files to process for '{rag_item.name}'.")
                for file_info in files_to_process:
                    await process_single_file(file_info, db, rag_item.id, rag_item.name)
                logger.info(f"Finished processing files for '{rag_item.name}'.")
            
            logger.info(f"--- Completed sync for RAG Item: '{rag_item.name}' (ID: {rag_item.id}) ---")

    except Exception as e:
        logger.error(f"An unexpected error occurred during the main sync task: {e}", exc_info=True)
    finally:
        db.close()
        logger.info("MinIO bucket synchronization task finished.")

